import pandas as pd
from io import BytesIO
from django.utils import timezone
from propertydata.models import *
from django.db.models import Q


class CustomExportResource:
    """
    Dynamically generates Excel data for a given CustomExportOptions instance.
    """
    def __init__(self, export_option):
        self.export_option = export_option

    def get_queryset(self):
        """
        Build a queryset that matches each ExportLeadFilter exactly.
        Avoids mixing states/types between filters.
        """
        filters = self.export_option.filter_option.all()
        q_objects = Q()

        for f in filters:
            q = Q(state=f.state)
            if f.sale_type:
                q &= Q(sale_type=f.sale_type)
            if f.sale_status:
                q &= Q(sale_status=f.sale_status)
            if f.surplus_status:
                q &= Q(surplus_status=f.surplus_status)
            q_objects |= q  # OR between filters, but AND inside each

        queryset = Foreclosure.objects.filter(q_objects).distinct()

        # Omit already delivered or old leads
        queryset = self.exclude_delivered_and_old(queryset)

        return queryset

    def exclude_delivered_and_old(self, queryset):
        """
        Remove old_leads and already delivered leads based on delivery_type.
        """
        export = self.export_option

        # Exclude old leads (always)
        queryset = queryset.exclude(pk__in=export.old_leads.values_list("pk", flat=True))

        # Exclude previously delivered ones of the same type
        if export.delivery_type == "pre-foreclosure":
            queryset = queryset.exclude(pk__in=export.pre_foreclosure.values_list("pk", flat=True))
        elif export.delivery_type == "post-foreclosure":
            queryset = queryset.exclude(pk__in=export.post_foreclosure.values_list("pk", flat=True))
        elif export.delivery_type == "verified":
            queryset = queryset.exclude(pk__in=export.verified_surplus.values_list("pk", flat=True))

        return queryset

    def to_dataframe(self):
        columns = self.export_option.columns or ["id", "state", "sale_type", "case_number", "sale_date"]
        queryset = self.get_queryset()
        data = list(queryset.values(*columns))
        return pd.DataFrame(data, columns=columns)

    def export_to_excel(self):
        df = self.to_dataframe()
        buffer = BytesIO()
        filename = f"{self.export_option.client_name}_{timezone.now().date()}.xlsx"

        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Leads")

        buffer.seek(0)
        return filename, buffer, df