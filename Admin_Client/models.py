from django.db import models
# from si_user.models import UserPayment


# Create your models here.
class Deliveries(models.Model):
    ASSIGNED = 'assigned'
    READY = 'ready'
    DELIVERED = 'delivered'
    REVISION = 'revision'
    STATUSCHOICES = (
        (ASSIGNED, 'Assigned'),
        (READY, 'Ready'),
        (DELIVERED, 'Delivered'),
        (REVISION, 'Revision')
        )
    delivery_date = models.DateField(null=True, blank=True)
    delivery_status = models.CharField(choices=STATUSCHOICES, max_length=100, blank=True, null=True)
    delivery_note = models.CharField(max_length=255, blank=True, null=True)
    delivered_in = models.DateField(null=True, blank=True)


class Orders(models.Model):
    RUNNING = 'running'
    COMPLETED = 'completed'
    STATUSCHOICES = (
    (RUNNING, 'Running'),
    (COMPLETED, 'Completed'),
    )

    
    REQUESTED = 'requested'
    IN_ESCROW = 'in_escrow'
    PAID = 'paid'
    NOT_PAID = 'not_paid'
    PAYMENTCHOICES = (
        (REQUESTED, 'Requested'),
        (IN_ESCROW, 'In Escrow'),
        (PAID, 'Paid'),
        (NOT_PAID, 'Not Paid')
    )
    date_ordered = models.DateField(blank=True, null=True)
    order_detail = models.CharField(max_length=255, blank=True)
    order_status = models.CharField(max_length=100, blank=True, choices=STATUSCHOICES)
    deliveries = models.ManyToManyField(Deliveries, blank=True)
    order_price = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    payment_method = models.CharField(max_length=255, blank=True, null=True)
    payment_status = models.CharField(max_length=100, blank=True, choices=PAYMENTCHOICES)
    transaction = models.ForeignKey('si_user.UserTransactions', on_delete=models.CASCADE, null=True, blank=True)


