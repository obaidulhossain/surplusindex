import pandas as pd
from io import BytesIO
from django.utils import timezone
from propertydata.models import *
from django.db.models import Q
from openpyxl import Workbook
from datetime import datetime
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import get_column_letter
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
        queryset = queryset.filter(published=True)
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
            "State": obj.state or "-",
            "county": obj.county or "-",
            "sale_type": obj.sale_type or "-",
            "sale_status": obj.sale_status or "-",
            "surplus_status": obj.surplus_status or "-",
            "case_number": obj.case_number or "-",
            "Sale Date": obj.sale_date or "-",
            "fcl_final_judgment": obj.fcl_final_judgment or "-",
            "sale_price": obj.sale_price or "-",
            "possible_surplus": obj.possible_surplus or "-",
            "verified_surplus": obj.verified_surplus or "-",
            "changed_at":obj.changed_at or "-",
            "lead_id":"",
            "confirmation_date":"",
            "foreclosure_deed":"-",
            "prior_deed":"-",
            "mailing_address_1":"-",          
        }

        # --- Handle Plaintiff (ManyToMany) -
        plaintiffs = obj.plaintiff.all() if hasattr(obj, "plaintiff") else []
        if plaintiffs:
            base["plaintiff"] = ", ".join([str(p) for p in plaintiffs if p]) or "-"
        else:
            base["plaintiff"] = "-"

        # --- Handle Defendant (ManyToMany) -
        defendants = obj.defendant.all() if hasattr(obj, "defendant") else []
        if defendants:
            first_defendant = defendants[0]
            other_defendants = defendants[1:]
            # Default placeholders
            base["defendant_first_name"] = "-"
            base["defendant_middle_name"] = "-"
            base["defendant_last_name"] = "-"
            base["additional_defendants"] = "-"
            # Check for business name first
            if first_defendant.business_name:
                base["defendant_first_name"] = str(first_defendant).strip()
            else:
                base["defendant_first_name"] = first_defendant.first_name.strip() if first_defendant.first_name else "-"
                base["defendant_middle_name"] = first_defendant.middle_name.strip() if first_defendant.middle_name else "-"
                base["defendant_last_name"] = first_defendant.last_name.strip() if first_defendant.last_name else "-"
            # Combine remaining defendants into one string
            if other_defendants:
                base["additional_defendants"] = ", ".join([str(d) for d in other_defendants if d]) or "-"
            base["defendant"] = ", ".join([str(d) for d in defendants if d]) or "-"
        else:
            base["defendant_first_name"] = "-"
            base["defendant_middle_name"] = "-"
            base["defendant_last_name"] = "-"
            base["additional_defendants"] = "-"
            base["defendant"] = "-"

        # --- Handle related property (ManyToMany) -
        STATE_ABBREVIATIONS = {
            "Alabama": "AL",
            "Alaska": "AK",
            "Arizona": "AZ",
            "Arkansas": "AR",
            "California": "CA",
            "Colorado": "CO",
            "Connecticut": "CT",
            "Delaware": "DE",
            "Florida": "FL",
            "Georgia": "GA",
            "Hawaii": "HI",
            "Idaho": "ID",
            "Illinois": "IL",
            "Indiana": "IN",
            "Iowa": "IA",
            "Kansas": "KS",
            "Kentucky": "KY",
            "Louisiana": "LA",
            "Maine": "ME",
            "Maryland": "MD",
            "Massachusetts": "MA",
            "Michigan": "MI",
            "Minnesota": "MN",
            "Mississippi": "MS",
            "Missouri": "MO",
            "Montana": "MT",
            "Nebraska": "NE",
            "Nevada": "NV",
            "New Hampshire": "NH",
            "New Jersey": "NJ",
            "New Mexico": "NM",
            "New York": "NY",
            "North Carolina": "NC",
            "North Dakota": "ND",
            "Ohio": "OH",
            "Oklahoma": "OK",
            "Oregon": "OR",
            "Pennsylvania": "PA",
            "Rhode Island": "RI",
            "South Carolina": "SC",
            "South Dakota": "SD",
            "Tennessee": "TN",
            "Texas": "TX",
            "Utah": "UT",
            "Vermont": "VT",
            "Virginia": "VA",
            "Washington": "WA",
            "West Virginia": "WV",
            "Wisconsin": "WI",
            "Wyoming": "WY",
            "District of Columbia": "DC",
        }
        first_property = obj.property.first() if hasattr(obj, "property") else None
        if first_property:
            state_name = first_property.state or "-"
            state_short = STATE_ABBREVIATIONS.get(state_name.strip(), "-")
            base["street_address"] = first_property.street_address or "-"
            base["city"] = first_property.city or "-"
            base["ST"] = state_short
            base["zip_code"] = first_property.zip_code or "-"
            base["parcel"] = first_property.parcel or "-"
        else:
            base["street_address"] = "-"
            base["city"] = "-"
            base["ST"] = "-"
            base["zip_code"] = "-"
            base["parcel"] = "-"

        # --- Add up to 5 contacts (defendants + related contacts) ---
        contacts = list(obj.defendant.all())

        # include related contacts of each defendant
        for d in obj.defendant.all():
            for rc in d.related_contacts.all():
                if rc not in contacts:
                    contacts.append(rc)

        # limit total to 5
        contacts = contacts[:5]

        for i in range(5):
            cnum = i + 1
            if i < len(contacts):
                contact = contacts[i]
                
                base[f"Contact Name {cnum}"] = str(contact) or "-"
                # pick up to 1 primary email or first 4 if you want more
                email_list = list(contact.emails.values_list("email_address", flat=True)[:4])
                base[f"Email {cnum}"] = ", ".join(email_list) if email_list else "-"

                # wireless numbers (up to 4)
                wireless_list = list(contact.wireless.values_list("w_number", flat=True)[:4])
                for j in range(4):
                    base[f"Wireless {cnum}.{j+1}"] = wireless_list[j] if j < len(wireless_list) else "-"

                # landline numbers (up to 4)
                landline_list = list(contact.landline.values_list("l_number", flat=True)[:4])
                for j in range(4):
                    base[f"Landline {cnum}.{j+1}"] = landline_list[j] if j < len(landline_list) else "-"
            else:
                # fill empty contact slots with "-"
                base[f"Contact Name {cnum}"] = "-"
                base[f"Email {cnum}"] = "-"
                for j in range(4):
                    base[f"Wireless {cnum}.{j+1}"] = "-"
                    base[f"Landline {cnum}.{j+1}"] = "-"

        return base

    def dehydrate_foreclosure_vertical(self, obj):
        """
        Generate multiple rows for each contact (defendants + related contacts),
        each row containing foreclosure info + single contact info.
        """
        base_info = {
            "id": obj.id,
            "State": obj.state or "-",
            "county": obj.county or "-",
            "sale_type": obj.sale_type or "-",
            "sale_status": obj.sale_status or "-",
            "surplus_status": obj.surplus_status or "-",
            "case_number": obj.case_number or "-",
            "Sale Date": obj.sale_date or "-",
            "possible_surplus": obj.possible_surplus or "-",
            "verified_surplus": obj.verified_surplus or "-",
            "fcl_final_judgment": obj.fcl_final_judgment or "-",
            "sale_price": obj.sale_price or "-",
            "changed_at":obj.changed_at or "-",
            "lead_id":"",
            "confirmation_date":"",
            "foreclosure_deed":"-",
            "prior_deed":"-",
            "mailing_address_1":"-",
        }

        # --- Handle Plaintiff (ManyToMany) -
        plaintiffs = obj.plaintiff.all() if hasattr(obj, "plaintiff") else []
        if plaintiffs:
            base_info["plaintiff"] = ", ".join([str(p) for p in plaintiffs if p]) or "-"
        else:
            base_info["plaintiff"] = "-"

        # --- Handle Defendant (ManyToMany) -
        defendants = obj.defendant.all() if hasattr(obj, "defendant") else []
        if defendants:
            first_defendant = defendants[0]
            other_defendants = defendants[1:]
            # Default placeholders
            base_info["defendant_first_name"] = "-"
            base_info["defendant_middle_name"] = "-"
            base_info["defendant_last_name"] = "-"
            base_info["additional_defendants"] = "-"
            # Check for business name first
            if first_defendant.business_name:
                base_info["defendant_first_name"] = str(first_defendant).strip()
            else:
                base_info["defendant_first_name"] = first_defendant.first_name.strip() if first_defendant.first_name else "-"
                base_info["defendant_middle_name"] = first_defendant.middle_name.strip() if first_defendant.middle_name else "-"
                base_info["defendant_last_name"] = first_defendant.last_name.strip() if first_defendant.last_name else "-"
            # Combine remaining defendants into one string
            if other_defendants:
                base_info["additional_defendants"] = ", ".join([str(d) for d in other_defendants if d]) or "-"
            base_info["defendant"] = ", ".join([str(d) for d in defendants if d]) or "-"
        else:
            base_info["defendant_first_name"] = "-"
            base_info["defendant_middle_name"] = "-"
            base_info["defendant_last_name"] = "-"
            base_info["additional_defendants"] = "-"
            base_info["defendant"] = "-"

        # --- Handle related property (ManyToMany) -
        STATE_ABBREVIATIONS = {
            "Alabama": "AL",
            "Alaska": "AK",
            "Arizona": "AZ",
            "Arkansas": "AR",
            "California": "CA",
            "Colorado": "CO",
            "Connecticut": "CT",
            "Delaware": "DE",
            "Florida": "FL",
            "Georgia": "GA",
            "Hawaii": "HI",
            "Idaho": "ID",
            "Illinois": "IL",
            "Indiana": "IN",
            "Iowa": "IA",
            "Kansas": "KS",
            "Kentucky": "KY",
            "Louisiana": "LA",
            "Maine": "ME",
            "Maryland": "MD",
            "Massachusetts": "MA",
            "Michigan": "MI",
            "Minnesota": "MN",
            "Mississippi": "MS",
            "Missouri": "MO",
            "Montana": "MT",
            "Nebraska": "NE",
            "Nevada": "NV",
            "New Hampshire": "NH",
            "New Jersey": "NJ",
            "New Mexico": "NM",
            "New York": "NY",
            "North Carolina": "NC",
            "North Dakota": "ND",
            "Ohio": "OH",
            "Oklahoma": "OK",
            "Oregon": "OR",
            "Pennsylvania": "PA",
            "Rhode Island": "RI",
            "South Carolina": "SC",
            "South Dakota": "SD",
            "Tennessee": "TN",
            "Texas": "TX",
            "Utah": "UT",
            "Vermont": "VT",
            "Virginia": "VA",
            "Washington": "WA",
            "West Virginia": "WV",
            "Wisconsin": "WI",
            "Wyoming": "WY",
            "District of Columbia": "DC",
        }

        # Handle related property
        first_property = obj.property.first() if hasattr(obj, "property") else None
        if first_property:
            state_name = first_property.state or "-"
            state_short = STATE_ABBREVIATIONS.get(state_name.strip(), "-")
            base_info.update({
                "street_address": first_property.street_address or "-",
                "city": first_property.city or "-",
                "ST": state_short,
                "zip_code": first_property.zip_code or "-",
                "parcel": first_property.parcel or "-"
            })
        else:
            base_info.update({
                "street_address": "-",
                "city": "-",
                "ST": "-",
                "zip_code": "-",
                "parcel": "-"
            })

        # Combine all contacts (defendants + related)
        contacts = list(obj.defendant.all())
        for d in obj.defendant.all():
            for rc in d.related_contacts.all():
                if rc not in contacts:
                    contacts.append(rc)

        contacts = contacts[:5]  # limit to 5

        rows = []
        if not contacts:
            # still create one row with blanks if no contact
            base_copy = base_info.copy()
            base_copy.update({
                "Contact Name": "-",
                "Email": "-",
                "Wireless 1": "-",
                "Wireless 2": "-",
                "Wireless 3": "-",
                "Wireless 4": "-",
                "Landline 1": "-",
                "Landline 2": "-",
                "Landline 3": "-",
                "Landline 4": "-",
            })
            rows.append(base_copy)
        else:
            for contact in contacts:
                contact_data = base_info.copy()
                contact_data["Contact Name"] = str(contact) or "-"

                # Emails
                email_list = list(contact.emails.values_list("email_address", flat=True)[:4])
                contact_data["Email"] = ", ".join(email_list) if email_list else "-"

                # Wireless
                wireless_list = list(contact.wireless.values_list("w_number", flat=True)[:4])
                #contact_data["Wireless"] = ", ".join(wireless_list) if wireless_list else "-"
                for j in range(4):
                    contact_data[f"Wireless {j+1}"] = wireless_list[j] if j < len(wireless_list) else "-"


                # Landline
                landline_list = list(contact.landline.values_list("l_number", flat=True)[:4])
                #contact_data["Landline"] = ", ".join(landline_list) if landline_list else "-"
                for j in range(4):
                    contact_data[f"Landline {j+1}"] = landline_list[j] if j < len(landline_list) else "-"

                rows.append(contact_data)

        return rows

    def to_dataframe(self):
        queryset = self.get_queryset()

        if getattr(self.export_option, "contact_align", "horizontal") == "vertical":
            queryset = queryset[:20]
            # Vertical mode: each contact gets its own row
            data = []
            for obj in queryset:
                data.extend(self.dehydrate_foreclosure_vertical(obj))
            df = pd.DataFrame(data)
        else:
            # Default horizontal mode (existing)
            data = [self.dehydrate_foreclosure(obj) for obj in queryset]
            df = pd.DataFrame(data)

        # Use selected columns if specified
        if self.export_option.columns:
            cols = [c for c in self.export_option.columns if c in df.columns]
            df = df[cols]

        return df


    # def to_dataframe(self):
    #     queryset = self.get_queryset()
    #     data = [self.dehydrate_foreclosure(obj) for obj in queryset]
    #     df = pd.DataFrame(data)

    #     # If user selected specific columns, use them.
    #     if self.export_option.columns:
    #         # Use only the requested columns that actually exist
    #         cols = [c for c in self.export_option.columns if c in df.columns]
    #         df = df[cols]
    #     else:
    #         # Default full fixed layout
    #         base_cols = [
    #             "id", "State", "county", "sale_type", "sale_status",
    #             "surplus_status", "case_number", "Sale Date", "plaintiff",
    #             "defendant", "street_address", "city", "zip_code",
    #             "parcel", "possible_surplus", "verified_surplus"
    #         ]
    #         contact_cols = []
    #         for i in range(1, 5):
    #             contact_cols.append(f"Contact Name {i}")
    #             contact_cols.append(f"Email {i}")
    #             for j in range(1, 5):
    #                 contact_cols.append(f"Wireless {i}.{j}")
    #             for j in range(1, 5):
    #                 contact_cols.append(f"Landline {i}.{j}")
    #         df = df[[c for c in base_cols + contact_cols if c in df.columns]]

    #     return df

    def export_to_excel(self):
        df = self.to_dataframe()
        buffer = BytesIO()
        filename = f"{self.export_option.client_name}_{timezone.now().date()}.xlsx"

        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Leads")

            # --- Style header after writing ---
            workbook = writer.book
            worksheet = writer.sheets["Leads"]

            # Header styling
            header_fill = PatternFill(start_color="516699", end_color="516699", fill_type="solid")  # blue background
            header_font = Font(color="FFFFFF", bold=True, size=12)  # white bold text
            header_align = Alignment(horizontal="center", vertical="center")

            # Apply style to all header cells
            for col_num, column_title in enumerate(df.columns, 1):
                cell = worksheet.cell(row=1, column=col_num)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = header_align
            # Optional: Auto-fit column width based on content
            max_length = max(
                (len(str(cell_value)) for cell_value in [column_title] + df[column_title].astype(str).tolist()),
                default=0
            )
            worksheet.column_dimensions[get_column_letter(col_num)].width = min(max_length + 2, 100)  # cap width


        buffer.seek(0)
        return filename, buffer, df










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


