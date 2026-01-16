from django.db import models

# Create your models here.
class SheriffAuction(models.Model):
    state = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    sale_date = models.DateField()

    case_number = models.CharField(max_length=50, unique=True)
    case_status = models.CharField(max_length=50)

    parcel = models.CharField(max_length=50, blank=True, null=True)
    property_address = models.TextField()
    fcl_final_judgment = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True
    )
    appraised_value = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    opening_bid = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    deposit = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    sold_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    sold_to = models.CharField(max_length=100, blank=True, null=True)

    scraped_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.case_number} – {self.property_address[:40]}"