# from django.core.mail import EmailMessage
# from import_export.formats.base_formats import XLSX
# from io import BytesIO
# from si_user.models import *
# from propertydata.models import *
# from Client.resources import ClientModelResource
# from django.conf import settings

# def generate_xlsx(leads):
#     """
#     Export Foreclosure leads queryset to XLSX in memory.
#     Returns a BytesIO object.
#     """
#     resources = ClientModelResource()
#     dataset = resources.export(leads)

#     xlsx_format = XLSX()
#     stream = BytesIO(xlsx_format.export_data(dataset))
#     stream.seek(0)
#     return stream


# def send_cycle_leads(task_instance):
#     """
#     Send foreclosure leads for a given task cycle
#     as XLSX attachment to all active subscribers.
#     """
#     # 1. Active subscriptions
#     active_subscriptions = StripeSubscription.objects.filter(
#         plan=task_instance.project.plan,
#         current_period_end__gte=task_instance.cycle.cycle_end
#     )
    
#     if not active_subscriptions.exists():
#         return
    
#     # 2. Leads within cycle date range
#     leads = Foreclosure.objects.filter(
#         state__iexact=task_instance.project.state,
#         published = True,
#         sale_date__range=(task_instance.cycle.sale_from, task_instance.cycle.sale_to)
#     )

#     if not leads.exists():
#         return

#     # 3. Generate XLSX once
#     xlsx_file = generate_xlsx(leads)
#     xlsx_bytes = xlsx_file.read()

#     # 4. Send per user
#     for sub in active_subscriptions:
#         user = sub.user
#         user_name = user.get_full_name() if hasattr(user, 'get_full_name') else user.username

#         subject = f"Leads Report for Cycle {task_instance.cycle.week}"
#         body = (
#             f"Hello {user_name},\n\n"
#             f"Please find attached the foreclosure leads between "
#             f"{task_instance.cycle.sale_from.strftime('%Y-%m-%d')} and "
#             f"{task_instance.cycle.sale_to.strftime('%Y-%m-%d')}.\n\n"
#             f"Best regards,\n"
#             f"SurplusIndex Team"
#         )

#         # Use a verified email for sending
#         email = EmailMessage(
#             subject=subject,
#             body=body,
#             from_email="contact@surplusindex.com",  # contact@surplusindex.com
#             to=[user.email],
#             reply_to="contact@surplusindex.com"   # optional
#         )

#         #Attach XLSX report
#         email.attach(
#             filename="leads_report.xlsx",
#             content=xlsx_bytes,
#             mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         )

#         try:
#             email.send(fail_silently=False)
#         except Exception as e:
#             print(f"Failed to send email to {user.email}: {e}")

from django.core.mail import EmailMessage
from import_export.formats.base_formats import XLSX
from io import BytesIO
from si_user.models import StripeSubscription
from propertydata.models import Foreclosure
from Client.resources import ClientModelResource
from django.conf import settings
import logging

# Set up logging for better error tracking
logger = logging.getLogger(__name__)

def generate_xlsx_bytes(leads):
    """
    Export Foreclosure leads queryset to XLSX in memory and return bytes.
    """
    resource = ClientModelResource()
    dataset = resource.export(leads)
    xlsx_format = XLSX()
    return xlsx_format.export_data(dataset)


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
    
    if not active_subscriptions.exists():
        logger.info("No active subscriptions found for this project plan.")
        return
    
    # 2. Leads within cycle date range
    leads = Foreclosure.objects.filter(
        state__iexact=task_instance.project.state,
        published=True,
        sale_date__range=(task_instance.cycle.sale_from, task_instance.cycle.sale_to)
    )

    if not leads.exists():
        logger.info("No leads found for the specified date range and state.")
        return

    # 3. Generate XLSX once outside the loop for efficiency
    try:
        xlsx_bytes = generate_xlsx_bytes(leads)
    except Exception as e:
        logger.error(f"Failed to generate XLSX file: {e}")
        return

    # 4. Send email to each user
    email_sender = settings.DEFAULT_FROM_EMAIL
    
    for sub in active_subscriptions:
        user = sub.user
        user_name = user.get_full_name() or user.username
        
        subject = f"Leads Report for Cycle {task_instance.cycle.week}"
        body = (
            f"Hello {user_name},\n\n"
            f"Please find attached the foreclosure leads between "
            f"{task_instance.cycle.sale_from.strftime('%Y-%m-%d')} and "
            f"{task_instance.cycle.sale_to.strftime('%Y-%m-%d')}.\n\n"
            f"Best regards,\n"
            f"SurplusIndex Team"
        )
        
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=email_sender,
            to=[user.email],
            reply_to=[email_sender]
        )
        
        email.attach(
            filename="leads_report.xlsx",
            content=xlsx_bytes,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        try:
            email.send(fail_silently=False)
            logger.info(f"Successfully sent email to {user.email}")
        except Exception as e:
            logger.error(f"Failed to send email to {user.email}: {e}")