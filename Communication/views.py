from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.urls import reverse

from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
import smtplib, imaplib, time, email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.utils.dateparse import parse_datetime
from django.utils import timezone
import pytz
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.db.models import F
from django.db.models.functions import Coalesce
from .utils import *
from .forms import *
from .models import *
from .tasks import *
from email.utils import formataddr
from realestate_directory.models import States
def ComDashboard(request):
    context = {
        "mail_accounts": MailAccount.objects.all(),
        "templates": MailTemplate.objects.all(),
        "contact_lists": ContactList.objects.all(),
    }
    return render(request, "Communication/communication.html", context)




def schedule_email_view(request):
    if request.method == "POST":
        sender_id = request.POST.get("sender")
        scope = request.POST.get("scope")
        recipient = request.POST.get("recipient")
        recipients_list = request.POST.get("recipients_list")
        contact_list_id = request.POST.get("contact_list") or None
        template_id = request.POST.get("template") or None
        custom_subject = request.POST.get("custom_subject")
        custom_body = request.POST.get("custom_body")
        send_mode = request.POST.get("send_mode")
        send_time = request.POST.get("send_time")

        if send_time:
            parsed_time = parse_datetime(send_time)  # parse string → datetime
            if parsed_time is None:
                raise ValueError("Invalid datetime format for send_time")
            # Localize to Dhaka timezone
            dhaka_tz = pytz.timezone("Asia/Dhaka")
            localized_time = dhaka_tz.localize(parsed_time)

            # Convert to UTC for storage
            utc_time = localized_time.astimezone(pytz.UTC)
        else:
            utc_time = timezone.now()
        sender = MailAccount.objects.get(id=sender_id)
        if contact_list_id == "all-clients":
            send_to_clients = True
            contact_list = None
        else:
            send_to_clients = False
            contact_list = ContactList.objects.filter(id=contact_list_id).first() if contact_list_id else None
        template = MailTemplate.objects.filter(id=template_id).first() if template_id else None
        subject = custom_subject or (template.subject if template else "")
        body = custom_body or (f"{template.body}\n\n{template.signature}" if template else "")
        html_body = body
        plain_body = strip_tags(html_body)

        if send_mode == "now":
            # Send immediately
            scheduled_email = ScheduledEmail(
                sender=sender,
                scope=scope,
                recipient=recipient if scope == "single" else None,
                recipients_list=recipients_list if scope == "multiple" else None,
                contact_list=contact_list,
                send_to_clients = send_to_clients,
                template=template,
                custom_subject=subject,
                custom_body=body,
                send_time=timezone.now(),
                status="pending"
            )
            sent_folder = "INBOX.Sent"
            imap = imaplib.IMAP4_SSL(sender.imap_host, sender.imap_port) if sender.use_ssl else imaplib.IMAP4(sender.imap_host, sender.imap_port)
            imap.login(sender.username, sender.password)

            # Format sender with display name
            from_email = formataddr((sender.name, sender.email_address))
            for r in scheduled_email.get_recipients():
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=plain_body,  # fallback plain text
                    from_email=from_email,
                    to=[r],
                    reply_to=[sender.email_address],
                )

                # Attach HTML version
                msg.attach_alternative(html_body, "text/html")
                # msg = EmailMessage(subject, body, from_email=from_email, to=[r], reply_to=[sender.email_address])
                msg.send(fail_silently=False)
                
                # Format message like RFC822 raw email
                raw_message = msg.message().as_bytes()
                imap.append(sent_folder, "\\Seen", None, raw_message)

            scheduled_email.status = "sent"
            scheduled_email.save()
            imap.logout()
        else:
            # Schedule later
            ScheduledEmail.objects.create(
                sender=sender,
                scope=scope,
                recipient=recipient if scope == "single" else None,
                recipients_list=recipients_list if scope == "multiple" else None,
                contact_list=contact_list,
                send_to_clients=send_to_clients,
                template=template,
                custom_subject=subject,
                custom_body=body,
                #send_time=send_time,
                send_time=utc_time,
                status="pending"
            )

        return redirect("com_dashboard")
    


    #     form = ScheduledEmailForm(request.POST)
    #     if form.is_valid():
    #         email_obj = form.save()
    #         if email_obj.send_time <= timezone.now():
    #             send_scheduled_email.delay(email_obj.id)  # immediate send
    #         else:
    #             send_scheduled_email.apply_async((email_obj.id,), eta=email_obj.send_time)  # schedule
    #         return redirect("email_list")  # Change to your dashboard/list view
    # else:
    #     form = ScheduledEmailForm()
    # return render(request, "Communication/schedule_email.html", {"form": form})

def ComContacts(request):
    params = request.POST if request.method == "POST" else request.GET
    selected_contact = params.get('contact_id')
    if selected_contact:
        contact_instance = ClientContact.objects.get(pk=selected_contact)
    else:
        contact_instance = None
    context = {
        "contacts": ClientContact.objects.all(),
        "contact_instance": contact_instance,
        "contact_lists": ContactList.objects.all(),
        "all_states": States.objects.all(),
    }
    return render(request, "Communication/contacts_lists.html", context)

def CreateUpdateClientContact(request):
    params = request.POST if request.method == "POST" else request.GET
    selected_contact = params.get('contact_id')
    name = params.get('name')
    email = params.get('email')
    phone = params.get('phone')
    business_name = params.get('business_name')
    address = params.get('address')
    if selected_contact:
        contact_instance = ClientContact.objects.get(pk=selected_contact)
        contact_instance.name = name
        contact_instance.email = email
        contact_instance.phone = phone
        contact_instance.business_name = business_name
        contact_instance.address = address
        contact_instance.save()
        messages.info(request, f"Contact Instance Updated ({contact_instance.name})")
    else:
        contact_instance = ClientContact.objects.update_or_create(
            name=name,
            email=email,
            defaults={
                "phone":phone,
                "business_name":business_name,
                "address":address,
            }
        )
        messages.success(request, f"Contact Instance Created ({contact_instance.name})")
    return redirect(f"{reverse('client_contacts')}?contact_id={contact_instance.id}")


@csrf_exempt
def manage_preferred_states(request, contact_id):
    if request.method == "POST":
        data = json.loads(request.body)
        state_ids = data.get("state_ids", [])
        action = data.get("action")

        try:
            contact = ClientContact.objects.get(id=contact_id)
        except ClientContact.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Contact not found"}, status=404)

        if action == "add":
            contact.preferred_states.add(*state_ids)
        elif action == "remove":
            contact.preferred_states.remove(*state_ids)

        return JsonResponse({
            "status": "success",
            "contact_id": contact_id,
            "action": action,
            "state_ids": state_ids
        })

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

def ComInbox(request):
    params = request.POST if request.method == "POST" else request.GET
    selected_email_id = params.get('selectedemail', '')

    if selected_email_id:
        EmailInstance = get_object_or_404(MailAccount, pk=selected_email_id)
        threads = (
            MailMessage.objects.filter(account=EmailInstance, folder="inbox")
            .order_by("-received_at")
            .values("thread_id")
            .distinct()
        )
        # For each thread, grab the latest message
        thread_messages = [
            MailMessage.objects.filter(thread_id=t["thread_id"], account=EmailInstance)
            .order_by("-received_at")
            .first()
            for t in threads
        ]
    else:
        EmailInstance = None
        thread_messages = None

    # Get only inbox messages, grouped by thread_id
    
    EmailAccounts = MailAccount.objects.all()

    context = {
        'EmailAccounts':EmailAccounts,
        'EmailInstance':EmailInstance,
        'thread_messages':thread_messages,
        
    }
    return render(request, "Communication/inbox.html", context)

@require_POST
def RefreshEmails(request):
    account_id = request.POST.get("account_id")
    account = get_object_or_404(MailAccount, pk=account_id)
    success, msg = fetch_emails(account)
    if success:
        messages.success(request, msg)
    else:
        messages.error(request, msg)
    return redirect(f"{reverse('com_inbox')}?selectedemail={account.id}")

@require_POST
def RefreshInboxFull(request):
    account_id = request.POST.get("account_id")
    account = get_object_or_404(MailAccount, pk=account_id)
    success, msg = fetch_folder(account, folder="INBOX", full_sync=True)
    if success:
        messages.success(request, msg)
    else:
        messages.error(request, msg)
    return redirect(f"{reverse('com_inbox')}?selectedemail={account.id}")

def conversation_view(request, thread_key, account_id ):
    account = get_object_or_404(MailAccount, pk=account_id)
    messages_qs = MailMessage.objects.filter(account=account, thread_key=thread_key).order_by("received_at")
    for msg in messages_qs:
        msg.is_read = True
        msg.save()
    first_message = messages_qs.first()
    context = {
        "account": account,
        "mails": messages_qs,
        "first_message": first_message,  # 👈 used for reply form
        "thread_key": thread_key,
    }
    return render(request, "Communication/conversation.html", context)

@require_POST
def toggle_read_status(request, msg_id):
    msg = get_object_or_404(MailMessage, id=msg_id)
    msg.is_read = not msg.is_read
    msg.save(update_fields=["is_read"])
    return JsonResponse({"success": True, "is_read": msg.is_read})

@require_POST
def edit_message_body(request, msg_id):
    msg = get_object_or_404(MailMessage, id=msg_id)
    new_body = request.POST.get("body", "").strip()
    if new_body:
        msg.body_plain = new_body
        msg.body_html = None  # keep it clean, plain text only
        msg.save(update_fields=["body_plain", "body_html"])
    return JsonResponse({"success": True, "body": msg.body_plain})

@require_POST
def send_reply_view(request, account_id, message_id):
    account = get_object_or_404(MailAccount, pk=account_id)
    parent_msg = get_object_or_404(MailMessage, pk=message_id, account=account)
    body = request.POST.get("body")

    if not body:
        messages.error(request, "Reply cannot be empty.")
        return redirect("conversation_view", account_id=account.id, thread_key=parent_msg.thread_key)

    try:
        reply_instance = send_reply(
            account=account,
            parent_msg=parent_msg,
            body=body,
            cc_addresses=None,
            bcc_addresses=None
        )
        if reply_instance:
            messages.success(request, "Reply sent successfully.")
        else:
            messages.warning(request, "Reply sent, but could not sync to database.")
    except Exception as e:
        messages.error(request, f"Failed to send reply: {e}")

    return redirect("conversation_view", account_id=account.id, thread_key=parent_msg.thread_key)

    
def archive_email(request, msg_id):
    if request.method == "POST":
        account_id = request.POST.get("account_id")
        account = get_object_or_404(MailAccount, id=account_id)
        msg = get_object_or_404(MailMessage, id=msg_id, account=account)

        try:
            # Connect IMAP
            if account.use_ssl:
                imap = imaplib.IMAP4_SSL(account.imap_host, account.imap_port)
            else:
                imap = imaplib.IMAP4(account.imap_host, account.imap_port)
            imap.login(account.username, account.password)
            imap.select("INBOX")
            
            result, _ = imap.uid("COPY", msg.uid, "INBOX.Archive")
            if result != "OK":
                raise Exception(f"Failed to copy to Archive")
            # Move to Archive
            # imap.uid("COPY", msg.uid, "Archived")
            imap.uid("STORE", msg.uid, "+FLAGS", "(\Deleted)")
            imap.expunge()
            imap.logout()

            # Update DB
            msg.folder = "archive"
            msg.save()
            messages.success(request, f"Message archived: {msg.subject}")
        except Exception as e:
            messages.error(request, f"Failed to archive: {e}")

    return redirect(f"{reverse('com_inbox')}?selectedemail={account.id}")

def delete_email(request, msg_id):
    if request.method == "POST":
        account_id = request.POST.get("account_id")
        account = get_object_or_404(MailAccount, id=account_id)
        msg = get_object_or_404(MailMessage, id=msg_id, account=account)

        try:
            # Connect IMAP
            if account.use_ssl:
                imap = imaplib.IMAP4_SSL(account.imap_host, account.imap_port)
            else:
                imap = imaplib.IMAP4(account.imap_host, account.imap_port)
            imap.login(account.username, account.password)
            imap.select(msg.folder.capitalize())  # select the folder where the mail currently is

            # Mark as deleted + expunge
            result, _ = imap.uid("COPY", msg.uid, "INBOX.Trash")
            if result != "OK":
                raise Exception(f"Failed to Delete")
            imap.uid("STORE", msg.uid, "+FLAGS", "(\Deleted)")
            imap.expunge()
            imap.logout()

            # Remove from DB
            msg.delete()
            messages.success(request, "Message deleted from server & DB.")
        except Exception as e:
            messages.error(request, f"Failed to delete: {e}")

    return redirect(f"{reverse('com_inbox')}?selectedemail={account.id}")



def ComSent(request):
    params = request.POST if request.method == "POST" else request.GET
    selected_email_id = params.get('selectedemail', '')

    if selected_email_id:
        EmailInstance = get_object_or_404(MailAccount, pk=selected_email_id)
        threads = (
            MailMessage.objects.filter(account=EmailInstance, folder="sent")
            .order_by("-sent_at")
            .values("thread_id")
            .distinct()
        )
        # For each thread, grab the latest message
        thread_messages = [
            MailMessage.objects.filter(thread_id=t["thread_id"], account=EmailInstance)
            .order_by("-sent_at")
            .first()
            for t in threads
        ]
    else:
        EmailInstance = None
        thread_messages = None

    # Get only inbox messages, grouped by thread_id
    
    EmailAccounts = MailAccount.objects.all()

    context = {
        'EmailAccounts':EmailAccounts,
        'EmailInstance':EmailInstance,
        'thread_messages':thread_messages,
        
    }
    return render(request, "Communication/sent.html", context)

@require_POST
def RefreshSentFull(request):
    account_id = request.POST.get("account_id")
    account = get_object_or_404(MailAccount, pk=account_id)
    success, msg = fetch_folder(account, folder="INBOX.Sent", full_sync=True)
    if success:
        messages.success(request, msg)
    else:
        messages.error(request, msg)
    return redirect(f"{reverse('com_sent')}?selectedemail={account.id}")

@require_POST
def RefreshSent(request):
    account_id = request.POST.get("account_id")
    account = get_object_or_404(MailAccount, pk=account_id)
    success, msg = fetch_folder(account, folder="INBOX.Sent")
    if success:
        messages.success(request, msg)
    else:
        messages.error(request, msg)
    return redirect(f"{reverse('com_sent')}?selectedemail={account.id}")


def archive_sent(request, msg_id):
    if request.method == "POST":
        account_id = request.POST.get("account_id")
        account = get_object_or_404(MailAccount, id=account_id)
        msg = get_object_or_404(MailMessage, id=msg_id, account=account)

        try:
            # Connect IMAP
            if account.use_ssl:
                imap = imaplib.IMAP4_SSL(account.imap_host, account.imap_port)
            else:
                imap = imaplib.IMAP4(account.imap_host, account.imap_port)
            imap.login(account.username, account.password)
            imap.select("INBOX.Sent")
            
            result, _ = imap.uid("COPY", msg.uid, "INBOX.Archive")
            if result != "OK":
                raise Exception(f"Failed to copy to Archive")
            # Move to Archive
            # imap.uid("COPY", msg.uid, "Archived")
            imap.uid("STORE", msg.uid, "+FLAGS", "(\Deleted)")
            imap.expunge()
            imap.logout()

            # Update DB
            msg.folder = "archive"
            msg.save()
            messages.success(request, f"Sent Message archived: {msg.subject}")
        except Exception as e:
            messages.error(request, f"Failed to archive sent message: {e}")

    return redirect(f"{reverse('com_sent')}?selectedemail={account.id}")

def delete_sent(request, msg_id):
    if request.method == "POST":
        account_id = request.POST.get("account_id")
        account = get_object_or_404(MailAccount, id=account_id)
        msg = get_object_or_404(MailMessage, id=msg_id, account=account)

        try:
            # Connect IMAP
            if account.use_ssl:
                imap = imaplib.IMAP4_SSL(account.imap_host, account.imap_port)
            else:
                imap = imaplib.IMAP4(account.imap_host, account.imap_port)
            imap.login(account.username, account.password)
            imap.select("INBOX.Sent")  # select the folder where the mail currently is

            # Mark as deleted + expunge
            result, _ = imap.uid("COPY", msg.uid, "INBOX.Trash")
            if result != "OK":
                raise Exception(f"Failed to Delete Sent Message")
            imap.uid("STORE", msg.uid, "+FLAGS", "(\Deleted)")
            imap.expunge()
            imap.logout()

            # Remove from DB
            msg.delete()
            messages.success(request, "Sent Message deleted from server & DB.")
        except Exception as e:
            messages.error(request, f"Failed to delete sent message: {e}")

    return redirect(f"{reverse('com_sent')}?selectedemail={account.id}")


def ComCampaign(request):
    log_path = "/home/priddxvk/logs/scheduled_emails.log"
    try:
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()[-200:]  # last 200 lines
    except FileNotFoundError:
        lines = ["Log file not found."]
    context = {
        "campaigns": ScheduledEmail.objects.all().order_by("-send_time"),
        "logs": lines,
    }
    return render(request, "Communication/campaign.html", context)

from django.http import FileResponse
def download_email_logs(request):
    log_path = "/home/priddxvk/logs/scheduled_emails.log"
    return FileResponse(open(log_path, "rb"), as_attachment=True, filename="scheduled_emails.log")

def clear_email_logs(request):
    log_path = "/home/priddxvk/logs/scheduled_emails.log"
    try:
        open(log_path, "w").close()
        messages.success(request, "Email logs cleared successfully.")
    except Exception as e:
        messages.error(request, f"Error clearing logs: {e}")
    return redirect("email_logs_view")

def ComTemplates(request):
    params = request.POST if request.method == "POST" else request.GET
    
    selected_template = params.get('selected_template', '')
    if selected_template:
        templateInstance = MailTemplate.objects.get(pk=selected_template)
    else:
        templateInstance = None
    templates = MailTemplate.objects.all()
    context = {
        "templates" : templates,
        "selected_template" :selected_template,
        "templateInstance" : templateInstance,
    }
    return render(request, "Communication/email_templates.html", context)
def createUpdateTemplate(request):
    if request.method == "POST":
        name = request.POST.get("name")
        subject = request.POST.get("subject")
        body = request.POST.get("body")
        signature = request.POST.get("signature")
        selected_template = request.POST.get('selected_template', '')
        if selected_template:
            templateInstance = MailTemplate.objects.get(pk=selected_template)
            if name:
                templateInstance.name = name
            if subject:
                templateInstance.subject = subject
            if body:
                templateInstance.body = body
            if signature:
                templateInstance.signature = signature
            templateInstance.save()
            messages.success(request, f"Template Instance {templateInstance.name} Saved!")
            return redirect(f"{reverse('com_templates')}?selectedtemplate={templateInstance.id}")
        else:
            if name and subject and body:  # basic validation
                templateInstance = MailTemplate.objects.create(
                    name=name,
                    subject=subject,
                    body=body,
                    signature=signature
                )
            messages.success(request, f"Template Instance {templateInstance.name} Created!")
            return redirect(f"{reverse('com_templates')}?selectedtemplate={templateInstance.id}")
    else:
        messages.error(request, "Post Method Required")
    return redirect('com_templates')
#-----------------------------------Communication Settings ---------------------------
def ComSettings(request):
    params = request.POST if request.method == "POST" else request.GET
    SelectedEmail = params.get('selectedemail', '')
    EmailInstance = None
    if SelectedEmail:
        EmailInstance = MailAccount.objects.get(pk=SelectedEmail)

    Emails = MailAccount.objects.all()
    context = {
        'Emails':Emails,
        'EmailInstance':EmailInstance,
    }
    return render(request, "Communication/com_settings.html", context)

def CreateUpdateEmailAc(request):
    params = request.POST if request.method == "POST" else request.GET
    selected_email_id = params.get('selectedemail', '')

    # Extract fields
    fields = {
        "name": params.get("name", "").strip(),
        "email_address": params.get("email", "").strip(),
        "smtp_host": params.get("smtp_host", "").strip(),
        "smtp_port": params.get("smtp_port", "").strip(),
        "username": params.get("username", "").strip(),
        "password": params.get("password", "").strip(),
        "use_tls": params.get("use_tls") in ["1", "true", "on", "True"],
        "use_ssl": params.get("use_ssl") in ["1", "true", "on", "True"],
        "imap_host": params.get("imap_host", "").strip(),
        "imap_port": params.get("imap_port", "").strip(),
    }
    if selected_email_id:
        # Update existing
        email_instance = get_object_or_404(MailAccount, pk=selected_email_id)
        for field, value in fields.items():
            if value != "":
                setattr(email_instance, field, value)
        email_instance.save()
        messages.success(request, f"Email {email_instance.email_address} updated!")
    else:
        # Create new
        email_instance, created = MailAccount.objects.get_or_create(
            email_address=fields["email_address"],
            defaults=fields,
        )
        if created:
            messages.success(request, f"Email {email_instance.email_address} created!")
        else:
            messages.info(request, f"Email {email_instance.email_address} already exists and was selected.")

    return redirect(f"{reverse('com_settings')}?selectedemail={email_instance.id}")
    

def DeleteEmailAccount(request):
    if request.method == "POST":
        Email = request.POST.get('selectedemail',"")
        if Email:
            EmailAccountInstance = MailAccount.objects.get(id=Email)
            email_address = EmailAccountInstance.email_address  # save before deleting
            EmailAccountInstance.delete()
            messages.success(request, f"Email Account: {email_address} Deleted!")
    return redirect('com_settings')
    
def TestEmailAccount(request, pk):
    email_account = get_object_or_404(MailAccount, pk=pk)
    success, message = test_email_connection(email_account)
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    return redirect('com_settings')


def send_mail_view(request):
    if request.method == "POST":
        subject = request.POST.get("subject")
        body = request.POST.get("body")
        recipient = request.POST.get("recipient")
        account_id = request.POST.get("account_id")

        account = MailAccount.objects.get(id=account_id)

        # Save in DB as queued
        mail = MailMessage.objects.create(
            account=account,
            subject=subject,
            body=body,
            sender=account.email_address,
            recipient=recipient,
            status="queued"
        )

        # Push to Celery
        send_mail_task.delay(mail.id)

        return redirect("mail_outbox")  # define your outbox view

    accounts = MailAccount.objects.all()
    return render(request, "Communication/send_mail.html", {"accounts": accounts})
