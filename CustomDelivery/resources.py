import pandas as pd
from io import BytesIO
from django.utils import timezone
from propertydata.models import *
from django.db.models import Q
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime

class CustomExportResource:
    """
    Dynamically generates Excel data for a given CustomExportOptions instance.
    Includes up to 4 related contacts with wireless & landline numbers.
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

    def dehydrate_foreclosure(self, obj):
        """
        Convert a Foreclosure instance into a dict with up to 4 contact groups.
        """
        base = {
            "id": obj.id,
            "state": obj.state or "-",
            "county": obj.county or "-",
            "sale_type": obj.sale_type or "-",
            "sale_status": obj.sale_status or "-",
            "surplus_status": obj.surplus_status or "-",
            "case_number": obj.case_number or "-",
            "sale_date": obj.sale_date or "-",
            # "plaintiff": obj.plaintiff or "-",
            # "defendant": obj.defendant or "-",
            "fcl_final_judgment": obj.fcl_final_judgment or "-",
            "sale_price": obj.sale_price or "-",
            "possible_surplus": obj.possible_surplus or "-",
            "verified_surplus": obj.verified_surplus or "-",
            
        }
        # --- Handle Plaintiff (ManyToMany) -
        plaintiffs = obj.plaintiff.all() if hasattr(obj, "plaintiff") else []
        if plaintiffs:
            base["plaintiff"] = ", ".join([p for p in plaintiffs if p]) or "-"
        else:
            base["plaintiff"] = "-"
        # --- Handle Defendant (ManyToMany) -
        defendants = obj.defendant.all() if hasattr(obj, "defendant") else []
        if defendants:
            base["defendant"] = ", ".join([d for d in defendants if d]) or "-"
        else:
            base["defendant"] = "-"

        # --- Handle related property (ManyToMany) -
        first_property = obj.property.first() if hasattr(obj, "property") else None
        if first_property:
            base["street_address"] = first_property.street_address or "-"
            base["city"] = first_property.city or "-"
            base["state"] = first_property.state or "-"
            base["zip_code"] = first_property.zip_code or "-"
            base["parcel"] = first_property.parcel or "-"
        else:
            base["street_address"] = "-"
            base["city"] = "-"
            base["state"] = "-"
            base["zip_code"] = "-"
            base["parcel"] = "-"

        # --- Add up to 4 related contacts ---
        related_contacts = list(obj.related_contacts.all()[:4])
        for i in range(4):
            cnum = i + 1
            if i < len(related_contacts):
                contact = related_contacts[i]
                base[f"Contact Name {cnum}"] = contact.full_name or "-"
                base[f"Email {cnum}"] = contact.email or "-"

                wireless_list = list(contact.wireless.values_list("number", flat=True)[:4])
                landline_list = list(contact.landline.values_list("number", flat=True)[:4])

                for j in range(4):
                    base[f"Wireless {cnum}.{j+1}"] = wireless_list[j] if j < len(wireless_list) else "-"
                    base[f"Landline {cnum}.{j+1}"] = landline_list[j] if j < len(landline_list) else "-"
            else:
                # fill empty contact slots with "-"
                base[f"Contact Name {cnum}"] = "-"
                base[f"Email {cnum}"] = "-"
                for j in range(4):
                    base[f"Wireless {cnum}.{j+1}"] = "-"
                    base[f"Landline {cnum}.{j+1}"] = "-"

        return base

    def to_dataframe(self):
        queryset = self.get_queryset()
        data = [self.dehydrate_foreclosure(obj) for obj in queryset]
        df = pd.DataFrame(data)

        # If user selected specific columns, use them.
        if self.export_option.columns:
            # Use only the requested columns that actually exist
            cols = [c for c in self.export_option.columns if c in df.columns]
            df = df[cols]
        else:
            # Default full fixed layout
            base_cols = [
                "id", "state", "county", "sale_type", "sale_status",
                "surplus_status", "case_number", "sale_date", "plaintiff",
                "defendant", "street_address", "city", "zip_code",
                "parcel", "possible_surplus", "verified_surplus"
            ]
            contact_cols = []
            for i in range(1, 5):
                contact_cols.append(f"Contact Name {i}")
                contact_cols.append(f"Email {i}")
                for j in range(1, 5):
                    contact_cols.append(f"Wireless {i}.{j}")
                for j in range(1, 5):
                    contact_cols.append(f"Landline {i}.{j}")
            df = df[[c for c in base_cols + contact_cols if c in df.columns]]

        return df

    def export_to_excel(self):
        df = self.to_dataframe()
        buffer = BytesIO()
        filename = f"{self.export_option.client_name}_{timezone.now().date()}.xlsx"

        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Leads")

        buffer.seek(0)
        return filename, buffer, df


    # def to_dataframe(self):
    #     columns = self.export_option.columns or ["id", "state", "sale_type", "case_number", "sale_date"]
    #     queryset = self.get_queryset()
    #     data = list(queryset.values(*columns))
    #     return pd.DataFrame(data, columns=columns)





















# class CustomExportResource:
#     def __init__(self, export_option):
#         self.export_option = export_option

#     def get_queryset(self):
#         """Fetch filtered leads excluding old & delivery-type-specific leads."""
#         filters = {
#             "state": self.export_option.state,
#             "sale_type": self.export_option.sale_type,
#             "sale_status": self.export_option.sale_status,
#             "surplus_status": self.export_option.surplus_status,
#         }

#         queryset = Foreclosure.objects.filter(**filters)

#         # ✅ Always exclude old leads
#         queryset = queryset.exclude(id__in=self.export_option.old_leads.values_list("id", flat=True))

#         # ✅ Exclude already delivered leads
#         if self.export_option.delivery_type == "pre-foreclosure":
#             queryset = queryset.exclude(id__in=self.export_option.pre_foreclosure.values_list("id", flat=True))
#         elif self.export_option.delivery_type == "post-foreclosure":
#             queryset = queryset.exclude(id__in=self.export_option.post_foreclosure.values_list("id", flat=True))
#         elif self.export_option.delivery_type == "verified":
#             queryset = queryset.exclude(id__in=self.export_option.verified_surplus.values_list("id", flat=True))

#         return queryset.distinct()

#     def export_to_excel(self):
#         queryset = self.get_queryset()
#         df = pd.DataFrame(list(queryset.values()))

#         if df.empty:
#             return None, None, df

#         # Create Workbook
#         wb = Workbook()
#         ws = wb.active
#         ws.title = "Exported Leads"

#         # Title/Header Section
#         title = f"{self.export_option.client_name} - {self.export_option.state} Leads Export"
#         ws.merge_cells("A1:H1")
#         ws["A1"] = title
#         ws["A1"].font = Font(bold=True, size=14)
#         ws["A1"].alignment = Alignment(horizontal="center")

#         # Column Headers
#         headers = list(df.columns)
#         ws.append(headers)

#         header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
#         header_font = Font(color="FFFFFF", bold=True)
#         thin_border = Border(left=Side(style="thin"), right=Side(style="thin"), top=Side(style="thin"), bottom=Side(style="thin"))

#         for col_num, column_title in enumerate(headers, 1):
#             cell = ws.cell(row=2, column=col_num)
#             cell.value = column_title
#             cell.font = header_font
#             cell.fill = header_fill
#             cell.alignment = Alignment(horizontal="center", vertical="center")
#             cell.border = thin_border

#         # Data Rows
#         for row_idx, row in enumerate(df.itertuples(index=False), 3):
#             for col_idx, value in enumerate(row, 1):
#                 cell = ws.cell(row=row_idx, column=col_idx, value=value)
#                 cell.alignment = Alignment(horizontal="left")
#                 cell.border = thin_border

#         # Auto-adjust column widths
#         for column_cells in ws.columns:
#             length = max(len(str(cell.value or "")) for cell in column_cells)
#             ws.column_dimensions[get_column_letter(column_cells[0].column)].width = length + 2

#         # Save to buffer
#         buffer = BytesIO()
#         wb.save(buffer)
#         buffer.seek(0)

#         filename = f"{self.export_option.client_name}_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
#         return filename, buffer, df



# class CustomExportResource:
#     """
#     Dynamically generates Excel data for a given CustomExportOptions instance.
#     """
#     def __init__(self, export_option):
#         self.export_option = export_option

#     def get_queryset(self):
#         """
#         Build a queryset that matches each ExportLeadFilter exactly.
#         Avoids mixing states/types between filters.
#         """
#         filters = self.export_option.filter_option.all()
#         q_objects = Q()

#         for f in filters:
#             q = Q(state=f.state)
#             if f.sale_type:
#                 q &= Q(sale_type=f.sale_type)
#             if f.sale_status:
#                 q &= Q(sale_status=f.sale_status)
#             if f.surplus_status:
#                 q &= Q(surplus_status=f.surplus_status)
#             q_objects |= q  # OR between filters, but AND inside each

#         queryset = Foreclosure.objects.filter(q_objects).distinct()

#         # Omit already delivered or old leads
#         queryset = self.exclude_delivered_and_old(queryset)

#         return queryset

#     def exclude_delivered_and_old(self, queryset):
#         """
#         Remove old_leads and already delivered leads based on delivery_type.
#         """
#         export = self.export_option

#         # Exclude old leads (always)
#         queryset = queryset.exclude(pk__in=export.old_leads.values_list("pk", flat=True))

#         # Exclude previously delivered ones of the same type
#         if export.delivery_type == "pre-foreclosure":
#             queryset = queryset.exclude(pk__in=export.pre_foreclosure.values_list("pk", flat=True))
#         elif export.delivery_type == "post-foreclosure":
#             queryset = queryset.exclude(pk__in=export.post_foreclosure.values_list("pk", flat=True))
#         elif export.delivery_type == "verified":
#             queryset = queryset.exclude(pk__in=export.verified_surplus.values_list("pk", flat=True))

#         return queryset

#     def to_dataframe(self):
#         columns = self.export_option.columns or ["id", "state", "sale_type", "case_number", "sale_date"]
#         queryset = self.get_queryset()
#         data = list(queryset.values(*columns))
#         return pd.DataFrame(data, columns=columns)

#     def export_to_excel(self):
#         df = self.to_dataframe()
#         buffer = BytesIO()
#         filename = f"{self.export_option.client_name}_{timezone.now().date()}.xlsx"

#         with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
#             df.to_excel(writer, index=False, sheet_name="Leads")

#         buffer.seek(0)
#         return filename, buffer, df


