import smtplib, ssl, imaplib, email, time, hashlib
from email.header import decode_header
from django.utils import timezone
from .models import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import timedelta
from datetime import datetime
from django.db.models import IntegerField
from django.db.models.functions import Cast
def test_email_connection(email_account):
    """
    Test SMTP connection for a given EmailAccount instance.
    Returns (success, message).
    """
    try:
        if email_account.use_ssl:
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(email_account.smtp_host, email_account.smtp_port, context=context)
        else:
            server = smtplib.SMTP(email_account.smtp_host, email_account.smtp_port)
            if email_account.use_tls:
                server.starttls()
        
        # Try login
        server.login(email_account.username, email_account.password)
        server.quit()
        return True, f"✅ Connection successful for {email_account.email_address}"
    
    except Exception as e:
        return False, f"❌ Connection failed for {email_account.email_address}: {str(e)}"

def decode_mime_words(s):
    """Helper to decode MIME encoded words like =?UTF-8?..."""
    if not s:
        return ""
    decoded = decode_header(s)
    return "".join(
        part.decode(enc or "utf-8", errors="ignore") if isinstance(part, bytes) else str(part)
        for part, enc in decoded
    )

def fetch_folder_crosscheck(mail_account, folder="INBOX"):
    """
    Fetch only missing emails by cross-checking UIDs between IMAP server and DB.
    Always safe, avoids duplicates, never misses messages.
    """

    # Map folder
    if folder.lower().startswith("inbox.sent"):
        msg_status = "sent"
        db_folder = "sent"
    else:
        msg_status = "queued"
        db_folder = "inbox"

    try:
        # Connect IMAP
        imap = imaplib.IMAP4_SSL(mail_account.imap_host, mail_account.imap_port) \
            if mail_account.use_ssl else imaplib.IMAP4(mail_account.imap_host, mail_account.imap_port)
        imap.login(mail_account.username, mail_account.password)
        imap.select(folder)

        # Get all UIDs from server
        status, data = imap.uid("search", None, "ALL")
        if status != "OK":
            return False, f"Search failed in {folder}"

        server_uids = {int(uid) for uid in data[0].split()} if data[0] else set()
        if not server_uids:
            return True, f"No messages found in {folder}"

        # Get all UIDs already in DB
        db_uids = set(
            MailMessage.objects.filter(account=mail_account, folder=db_folder)
            .annotate(uid_int=Cast("uid", IntegerField()))
            .values_list("uid_int", flat=True)
        )

        # Find missing UIDs
        missing_uids = sorted(server_uids - db_uids)
        if not missing_uids:
            imap.close()
            imap.logout()
            return True, f"No new messages in {folder}"

        # Fetch missing emails
        for uid in missing_uids:
            status, msg_data = imap.uid("fetch", str(uid), "(RFC822 INTERNALDATE)")
            if status != "OK" or not msg_data:
                continue

            raw_email, internaldate = None, None
            for part in msg_data:
                if isinstance(part, tuple) and len(part) >= 2:
                    raw_email = part[1]
                    try:
                        internaldate = imaplib.Internaldate2tuple(part[0])
                    except Exception:
                        internaldate = None
            if not raw_email:
                # fallback: fetch only RFC822 if above failed
                status, msg_data = imap.uid("fetch", uid, "(RFC822)")
                if status == "OK" and msg_data and isinstance(msg_data[0], tuple):
                    raw_email = msg_data[0][1]

            if not raw_email:
                continue

            msg = email.message_from_bytes(raw_email)

            # Dates
            imap_date = None
            if internaldate:
                try:
                    imap_date = timezone.make_aware(
                        datetime.fromtimestamp(email.utils.mktime_tz(internaldate)),
                        timezone.get_current_timezone()
                    )
                except Exception:
                    imap_date = None

            header_date = None
            if msg.get("Date"):
                try:
                    header_date = email.utils.parsedate_to_datetime(msg.get("Date"))
                    if header_date and header_date.tzinfo is None:
                        header_date = timezone.make_aware(header_date, timezone.get_current_timezone())
                except Exception:
                    pass

            msg_date = header_date if folder.lower().startswith("inbox.sent") else imap_date or header_date

            # Extract headers
            subject = decode_mime_words(msg.get("Subject"))
            message_id = msg.get("Message-ID")
            in_reply_to_id = msg.get("In-Reply-To")
            sender = email.utils.parseaddr(msg.get("From"))[1]
            recipient = ", ".join([addr[1] for addr in email.utils.getaddresses(msg.get_all("To", []))])
            cc = ", ".join([addr[1] for addr in email.utils.getaddresses(msg.get_all("Cc", []))])
            bcc = ", ".join([addr[1] for addr in email.utils.getaddresses(msg.get_all("Bcc", []))])

            # Extract body
            body_plain, body_html = "", ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    try:
                        payload = part.get_payload(decode=True)
                        if not payload:
                            continue
                        if content_type == "text/plain":
                            body_plain += payload.decode(errors="ignore")
                        elif content_type == "text/html":
                            body_html += payload.decode(errors="ignore")
                    except Exception:
                        continue
            else:
                try:
                    body_plain = msg.get_payload(decode=True).decode(errors="ignore")
                except Exception:
                    body_plain = msg.get_payload()

            # Threading
            parent_msg = None
            thread_key = None
            if in_reply_to_id:
                parent_msg = MailMessage.objects.filter(message_id=in_reply_to_id, account=mail_account).first()
                if parent_msg:
                    thread_key = parent_msg.thread_key
            if not thread_key:
                base_id = message_id or str(uid)
                thread_key = hashlib.sha1(base_id.encode()).hexdigest()
            thread_id = parent_msg.thread_id if parent_msg else (message_id or str(uid))

            # Save
            MailMessage.objects.update_or_create(
                uid=uid,
                account=mail_account,
                folder=db_folder,
                defaults={
                    "subject": subject,
                    "sender": sender,
                    "recipient": recipient,
                    "cc": cc or None,
                    "bcc": bcc or None,
                    "received_at": msg_date,
                    "sent_at": msg_date,
                    "body_plain": body_plain,
                    "body_html": body_html,
                    "message_id": message_id,
                    "in_reply_to": parent_msg,
                    "thread_id": thread_id,
                    "thread_key": thread_key,
                    "status": msg_status,
                },
            )

        imap.close()
        imap.logout()
        return True, f"Fetched {len(missing_uids)} new messages from {folder}"

    except Exception as e:
        return False, str(e)

def send_reply(
    account: MailAccount,
    parent_msg: MailMessage,
    body: str,
    cc_addresses: list = None,
    bcc_addresses: list = None,
    folder: str = "INBOX.Sent",
    save_to_db: bool = True
    ):
    """
    Send a reply email that keeps the original thread_key.
    """

    # ---- Build reply ----
    msg = MIMEMultipart("alternative")
    msg["From"] = account.email_address
    msg["To"] = parent_msg.sender
    msg["Subject"] = f"Re: {parent_msg.subject}"
    msg["Message-ID"] = email.utils.make_msgid()
    msg["In-Reply-To"] = parent_msg.message_id
    msg["References"] = parent_msg.message_id
    msg["Reply-To"] = account.email_address

    if cc_addresses:
        msg["Cc"] = ", ".join(cc_addresses)

    part1 = MIMEText(body, "plain")
    msg.attach(part1)

    raw_message = msg.as_string()
    all_recipients = [parent_msg.sender] + (cc_addresses or []) + (bcc_addresses or [])

    # ---- Send via SMTP ----
    if account.use_tls:
        server = smtplib.SMTP(account.smtp_host, account.smtp_port)
        server.starttls()
    else:
        server = smtplib.SMTP_SSL(account.smtp_host, account.smtp_port)
    server.login(account.username, account.password)
    server.sendmail(account.email_address, all_recipients, raw_message)
    server.quit()

    # ---- Append to Sent folder ----
    if account.use_ssl:
        imap = imaplib.IMAP4_SSL(account.imap_host, account.imap_port)
    else:
        imap = imaplib.IMAP4(account.imap_host, account.imap_port)
    imap.login(account.username, account.password)
    imap.append(folder, "\\Seen", imaplib.Time2Internaldate(time.time()), raw_message.encode("utf-8"))

    # ---- Fetch latest UID from Sent folder ----
    imap.select(folder)
    status, data = imap.search(None, "ALL")
    latest_uid = data[0].split()[-1]
    status, msg_data = imap.uid("fetch", latest_uid, "(RFC822)")
    imap.logout()

    if status != "OK":
        return None

    raw_email = msg_data[0][1]
    sent_msg = email.message_from_bytes(raw_email)

    # ---- Keep same thread_key ----
    thread_key = parent_msg.thread_key

    # ---- Save to DB ----
    if save_to_db:
        reply_instance, _ = MailMessage.objects.update_or_create(
            uid=latest_uid.decode(),
            account=account,
            folder="sent",
            defaults={
                "subject": sent_msg.get("Subject"),
                "sender": account.email_address,
                "recipient": parent_msg.sender,
                "cc": ", ".join(cc_addresses) if cc_addresses else None,
                "bcc": ", ".join(bcc_addresses) if bcc_addresses else None,
                "received_at": timezone.now(),
                "body_plain": body,
                "body_html": None,
                "message_id": sent_msg.get("Message-ID"),
                "in_reply_to": parent_msg,
                "thread_id": parent_msg.thread_id,
                "thread_key": thread_key,
                "sent_at": timezone.now(),
                "status": "sent",
                "is_read": True,
            }
        )
        return reply_instance

    return None


# def fetch_folder(mail_account, folder="INBOX", full_sync=False, days=None):
#     """
#     use  = fetch_folder(account, folder="INBOX.Sent", full_sync=True, days=30)
#     Fetch emails for any folder (INBOX, Sent, etc.)
#     - full_sync=True → fetch ALL or last `days` messages
#     - full_sync=False → fetch only new messages since last UID
#     """
#     # Decide which field to use
#     if folder.lower().startswith("inbox.sent"):  
#         msg_status = "sent"
#         db_folder = "sent"
#     else:
#         msg_status = "queued"
#         db_folder = "inbox"
#     try:
#         # Connect IMAP
#         imap = imaplib.IMAP4_SSL(mail_account.imap_host, mail_account.imap_port) \
#             if mail_account.use_ssl else imaplib.IMAP4(mail_account.imap_host, mail_account.imap_port)
#         imap.login(mail_account.username, mail_account.password)
#         imap.select(folder)

#         # Decide search criteria
#         if full_sync:
#             if days:  # backfill only recent days
#                 since_date = (timezone.now() - timedelta(days=days)).strftime("%d-%b-%Y")
#                 search_criteria = f'(SINCE {since_date})'
#             else:  # full ALL fetch
#                 search_criteria = "ALL"
#         else:
#             last_uid = (
#                 MailMessage.objects.filter(account=mail_account, folder=db_folder)
#                 .annotate(uid_int=Cast("uid", IntegerField()))   # force int
#                 .order_by("-uid_int")
#                 .values_list("uid_int", flat=True)
#                 .first()
#             )
#             search_criteria = f"UID {int(last_uid)+1}:*" if last_uid else "ALL"

#         # Fetch UIDs
#         status, data = imap.uid("search", None, search_criteria)
#         if status != "OK":
#             return False, f"Search failed in {folder}"
#         new_uids = data[0].split()
#         if not new_uids:
#             return True, f"No new messages in {folder}"

#         for uid in new_uids:
#             uid = uid.decode()

#             # Fetch full message
#             status, msg_data = imap.uid("fetch", uid, "(RFC822 INTERNALDATE)")
#             if status != "OK" or not msg_data:
#                 continue
            
#             raw_email = None
#             internaldate = None

#             for part in msg_data:
#                 if isinstance(part, tuple) and len(part) >= 2:
#                     raw_email = part[1]  # the actual RFC822 message
#                     try:
#                         internaldate = imaplib.Internaldate2tuple(part[0])
#                     except Exception:
#                         internaldate = None

#             if not raw_email:
#                 # fallback: fetch only RFC822 if above failed
#                 status, msg_data = imap.uid("fetch", uid, "(RFC822)")
#                 if status == "OK" and msg_data and isinstance(msg_data[0], tuple):
#                     raw_email = msg_data[0][1]
            
#             if not raw_email:
#                 continue  # skip this UID if we still don’t have a message

#             msg = email.message_from_bytes(raw_email)
            
#             imap_date = None
#             if internaldate:
#                 try:
#                     imap_date = timezone.make_aware(
#                         datetime.fromtimestamp(email.utils.mktime_tz(internaldate)),
#                         timezone.get_current_timezone()
#                     )
#                 except Exception:
#                     imap_date = None
            
#             # Fallback to header Date
#             header_date = None
#             if msg.get("Date"):
#                 try:
#                     header_date = email.utils.parsedate_to_datetime(msg.get("Date"))
#                     if header_date and header_date.tzinfo is None:
#                         header_date = timezone.make_aware(header_date, timezone.get_current_timezone())
#                 except Exception:
#                     pass


#             # Extract headers
#             subject = decode_mime_words(msg.get("Subject"))
#             message_id = msg.get("Message-ID")
#             in_reply_to_id = msg.get("In-Reply-To")
#             sender = email.utils.parseaddr(msg.get("From"))[1]
#             recipient = ", ".join([addr[1] for addr in email.utils.getaddresses(msg.get_all("To", []))])
#             cc = ", ".join([addr[1] for addr in email.utils.getaddresses(msg.get_all("Cc", []))])
#             bcc = ", ".join([addr[1] for addr in email.utils.getaddresses(msg.get_all("Bcc", []))])
            
#             # Parse message date
#             # Decide which to use
#             if folder.lower().startswith("inbox.sent"):
#                 msg_date = header_date or imap_date  # Prefer "Date" for Sent
#             else:
#                 msg_date = imap_date or header_date  # Prefer server date for Inbox
                
#             #msg_date = email.utils.parsedate_to_datetime(msg.get("Date")) if msg.get("Date") else timezone.now()

            
            

#             # Extract body
#             body_plain, body_html = "", ""
#             if msg.is_multipart():
#                 for part in msg.walk():
#                     content_type = part.get_content_type()
#                     try:
#                         payload = part.get_payload(decode=True)
#                         if not payload:
#                             continue
#                         if content_type == "text/plain":
#                             body_plain += payload.decode(errors="ignore")
#                         elif content_type == "text/html":
#                             body_html += payload.decode(errors="ignore")
#                     except Exception:
#                         continue
#             else:
#                 try:
#                     body_plain = msg.get_payload(decode=True).decode(errors="ignore")
#                 except Exception:
#                     body_plain = msg.get_payload()

#             # Threading
#             parent_msg = None
#             thread_key = None
#             if in_reply_to_id:
#                 parent_msg = MailMessage.objects.filter(message_id=in_reply_to_id, account=mail_account).first()
#                 if parent_msg:
#                     thread_key = parent_msg.thread_key
#             if not thread_key:
#                 base_id = message_id or uid
#                 thread_key = hashlib.sha1(base_id.encode()).hexdigest()
#             thread_id = parent_msg.thread_id if parent_msg else (message_id or uid)

#             # Save
#             MailMessage.objects.update_or_create(
#                 uid=uid,
#                 account=mail_account,
#                 folder=db_folder,
#                 defaults={
#                     "subject": subject,
#                     "sender": sender,
#                     "recipient": recipient,
#                     "cc": cc or None,
#                     "bcc": bcc or None,
#                     "received_at": msg_date,
#                     "sent_at": msg_date,
#                     "body_plain": body_plain,
#                     "body_html": body_html,
#                     "message_id": message_id,
#                     "in_reply_to": parent_msg,
#                     "thread_id": thread_id,
#                     "thread_key": thread_key,
#                     "status": msg_status,
#                     # "is_read": False,
#                 },
#             )

#         imap.close()
#         imap.logout()
#         return True, f"Fetched {len(new_uids)} messages from {folder}"

#     except Exception as e:
#         return False, str(e)