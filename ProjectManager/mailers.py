from django.core.mail import EmailMessage
from import_export.formats.base_formats import XLSX
from io import BytesIO
from si_user.models import *
from propertydata.models import *
from Client.resources import ClientModelResource
from django.conf import settings







def generate_xlsx(leads):
    """
    Export Foreclosure leads queryset to XLSX in memory.
    Returns a BytesIO object.
    """
    resources = ClientModelResource()
    dataset = resources.export(leads)

    xlsx_format = XLSX()
    stream = BytesIO(xlsx_format.export_data(dataset))
    stream.seek(0)
    return stream


def send_cycle_leads(task_instance):
    """
    Send foreclosure leads for a given task cycle
    as XLSX attachment to all active subscribers.
    """
    # 1. Active subscriptions
    active_subscriptions = StripeSubscription.objects.filter(
        plan=task_instance.project.plan,
        current_period_end__gte=task_instance.cycle.cycle_end
    )

    # 2. Leads within cycle date range
    leads = Foreclosure.objects.filter(
        state__iexact=task_instance.project.state,
        published = True,
        sale_date__range=(task_instance.cycle.sale_from, task_instance.cycle.sale_to)
    )

    if not leads.exists():
        return

    # 3. Generate XLSX once
    xlsx_file = generate_xlsx(leads)
    xlsx_bytes = xlsx_file.read()

    # 4. Send per user
    for sub in active_subscriptions:
        user = sub.user

        subject = f"Leads Report for Cycle {task_instance.cycle.week}"
        body = (
            f"Hello {getattr(user, 'get_full_name', lambda: user.username)()},\n\n"
            f"Please find attached the foreclosure leads between "
            f"{task_instance.cycle.sale_from.strftime('%Y-%m-%d')} and "
            f"{task_instance.cycle.sale_to.strftime('%Y-%m-%d')}.\n\n"
            f"Best regards,\nYour Team"
        )

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.EMAIL_HOST_USER,
            to=[user.email],
        )
        email.attach(
            "leads_report.xlsx",
            xlsx_bytes,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            
        )
        email.send(fail_silently=False)













from import_export.formats.base_formats import XLSX
from io import BytesIO
from Client.resources import *


def generate_xlsx(leads):
    resources = ClientModelResource()
    dataset = resources.export(leads)

    # Convert dataset to XLSX
    xlsx_format = XLSX()
    # Save into memory as file-like object
    stream = BytesIO(xlsx_format.export_data(dataset))
    stream.seek(0)
    return stream

def send_cycle_leads(task_instance):
    active_subscriptions = StripeSubscription.objects.filter(
        plan=task_instance.project.plan,
        current_period_end__gte=task_instance.cycle.cycle_end
    )

    leads = Foreclosure.objects.filter(
        sale_date__range=(task_instance.cycle.sale_from, task_instance.cycle.sale_to)
    )

    if not leads.exists():
        return

    # Generate XLSX file once
    xlsx_file = generate_xlsx(leads)
    xlsx_bytes = xlsx_file.read()

    for sub in active_subscriptions:
        user = sub.user

        subject = f"Leads Report for Cycle {task_instance.cycle.id}"
        body = (
            f"Hello {user.get_full_name() if hasattr(user, 'get_full_name') else user.username},\n\n"
            f"Please find attached the foreclosure leads between "
            f"{task_instance.cycle.sale_from.strftime('%Y-%m-%d')} and "
            f"{task_instance.cycle.sale_to.strftime('%Y-%m-%d')}.\n\n"
            f"Best regards,\nYour Team"
        )

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email="noreply@yourdomain.com",
            to=[user.email],
        )
        email.attach(
            "leads_report.xlsx",
            xlsx_bytes,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        email.send()