# import smtplib
# from email.mime.text import MIMEText

# # Email settings
# SMTP_SERVER = "surplusindex.com"  # Replace with your SMTP host
# SMTP_PORT = 465                      # Replace with your SMTP port
# EMAIL_USER = "contact@surplusindex.com"  # Replace with your email
# EMAIL_PASS = "Surplusindex@pc11c"     # Replace with your email password

# # Message
# msg = MIMEText("This is a test email.")
# msg["Subject"] = "Test Email"
# msg["From"] = EMAIL_USER
# msg["To"] = "obaidulbiplob.bd@gmail.com"

# try:
#     with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:  # Use SMTP_SSL for port 465
#         server.login(EMAIL_USER, EMAIL_PASS)
#         server.send_message(msg)
#         print("Email sent successfully!")
# except Exception as e:
#     print(f"Failed to send email: {e}")
