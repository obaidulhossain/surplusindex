from django.shortcuts import render, redirect
from django.utils import timezone
from .models import MailMessage, MailAccount
from .tasks import send_mail_task

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
