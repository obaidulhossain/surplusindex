from import_export import resources, fields
from propertydata.models import *

class ClientModelResource(resources.ModelResource):
    DateListed = fields.Field(column_name='Date Listed')
    LastReported = fields.Field(column_name='Last Reported')
    CaseNumber = fields.Field(column_name='CaseNumber')
    Plaintiff = fields.Field(column_name='Plaintiff')
    Defendant = fields.Field(column_name='Defendant')
    parcel_id = fields.Field(column_name='parcel_id')
    StreetAddress = fields.Field(column_name='Street Address')
    City = fields.Field(column_name='City')
    Zip = fields.Field(column_name='Zip')

    ContactName1 = fields.Field(column_name='Contact Name 1')
    email1 = fields.Field(column_name='Email 1')
    landline1_1 = fields.Field(column_name='Landline 1.1')
    landline1_2 = fields.Field(column_name='Landline 1.2')
    landline1_3 = fields.Field(column_name='Landline 1.3')
    landline1_4 = fields.Field(column_name='Landline 1.4')
    wireless1_1 = fields.Field(column_name='Wireless 1.1')
    wireless1_2 = fields.Field(column_name='Wireless 1.2')
    wireless1_3 = fields.Field(column_name='Wireless 1.3')
    wireless1_4 = fields.Field(column_name='Wireless 1.4')

    ContactName2 = fields.Field(column_name='Contact Name 2')
    email2 = fields.Field(column_name='Email 2')
    landline2_1 = fields.Field(column_name='Landline 2.1')
    landline2_2 = fields.Field(column_name='Landline 2.2')
    landline2_3 = fields.Field(column_name='Landline 2.3')
    landline2_4 = fields.Field(column_name='Landline 2.4')
    wireless2_1 = fields.Field(column_name='Wireless 2.1')
    wireless2_2 = fields.Field(column_name='Wireless 2.2')
    wireless2_3 = fields.Field(column_name='Wireless 2.3')
    wireless2_4 = fields.Field(column_name='Wireless 2.4')

    ContactName3 = fields.Field(column_name='Contact Name 3')
    email3 = fields.Field(column_name='Email 3')
    landline3_1 = fields.Field(column_name='Landline 3.1')
    landline3_2 = fields.Field(column_name='Landline 3.2')
    landline3_3 = fields.Field(column_name='Landline 3.3')
    landline3_4 = fields.Field(column_name='Landline 3.4')
    wireless3_1 = fields.Field(column_name='Wireless 3.1')
    wireless3_2 = fields.Field(column_name='Wireless 3.2')
    wireless3_3 = fields.Field(column_name='Wireless 3.3')
    wireless3_4 = fields.Field(column_name='Wireless 3.4')

    ContactName4 = fields.Field(column_name='Contact Name 4')
    email4 = fields.Field(column_name='Email 4')
    landline4_1 = fields.Field(column_name='Landline 4.1')
    landline4_2 = fields.Field(column_name='Landline 4.2')
    landline4_3 = fields.Field(column_name='Landline 4.3')
    landline4_4 = fields.Field(column_name='Landline 4.4')
    wireless4_1 = fields.Field(column_name='Wireless 4.1')
    wireless4_2 = fields.Field(column_name='Wireless 4.2')
    wireless4_3 = fields.Field(column_name='Wireless 4.3')
    wireless4_4 = fields.Field(column_name='Wireless 4.4')

    ContactName5 = fields.Field(column_name='Contact Name 5')
    email5 = fields.Field(column_name='Email 5')
    landline5_1 = fields.Field(column_name='Landline 5.1')
    landline5_2 = fields.Field(column_name='Landline 5.2')
    landline5_3 = fields.Field(column_name='Landline 5.3')
    landline5_4 = fields.Field(column_name='Landline 5.4')
    wireless5_1 = fields.Field(column_name='Wireless 5.1')
    wireless5_2 = fields.Field(column_name='Wireless 5.2')
    wireless5_3 = fields.Field(column_name='Wireless 5.3')
    wireless5_4 = fields.Field(column_name='Wireless 5.4')

    ContactName6 = fields.Field(column_name='Contact Name 6')
    email6 = fields.Field(column_name='Email 6')
    landline6_1 = fields.Field(column_name='Landline 6.1')
    landline6_2 = fields.Field(column_name='Landline 6.2')
    landline6_3 = fields.Field(column_name='Landline 6.3')
    landline6_4 = fields.Field(column_name='Landline 6.4')
    wireless6_1 = fields.Field(column_name='Wireless 6.1')
    wireless6_2 = fields.Field(column_name='Wireless 6.2')
    wireless6_3 = fields.Field(column_name='Wireless 6.3')
    wireless6_4 = fields.Field(column_name='Wireless 6.4')

    ContactName7 = fields.Field(column_name='Contact Name 7')
    email7 = fields.Field(column_name='Email 7')
    landline7_1 = fields.Field(column_name='Landline 7.1')
    landline7_2 = fields.Field(column_name='Landline 7.2')
    landline7_3 = fields.Field(column_name='Landline 7.3')
    landline7_4 = fields.Field(column_name='Landline 7.4')
    wireless7_1 = fields.Field(column_name='Wireless 7.1')
    wireless7_2 = fields.Field(column_name='Wireless 7.2')
    wireless7_3 = fields.Field(column_name='Wireless 7.3')
    wireless7_4 = fields.Field(column_name='Wireless 7.4')

    ContactName8 = fields.Field(column_name='Contact Name 8')
    email8 = fields.Field(column_name='Email 8')
    landline8_1 = fields.Field(column_name='Landline 8.1')
    landline8_2 = fields.Field(column_name='Landline 8.2')
    landline8_3 = fields.Field(column_name='Landline 8.3')
    landline8_4 = fields.Field(column_name='Landline 8.4')
    wireless8_1 = fields.Field(column_name='Wireless 8.1')
    wireless8_2 = fields.Field(column_name='Wireless 8.2')
    wireless8_3 = fields.Field(column_name='Wireless 8.3')
    wireless8_4 = fields.Field(column_name='Wireless 8.4')

    ContactName9 = fields.Field(column_name='Contact Name 9')
    email9 = fields.Field(column_name='Email 9')
    landline9_1 = fields.Field(column_name='Landline 9.1')
    landline9_2 = fields.Field(column_name='Landline 9.2')
    landline9_3 = fields.Field(column_name='Landline 9.3')
    landline9_4 = fields.Field(column_name='Landline 9.4')
    wireless9_1 = fields.Field(column_name='Wireless 9.1')
    wireless9_2 = fields.Field(column_name='Wireless 9.2')
    wireless9_3 = fields.Field(column_name='Wireless 9.3')
    wireless9_4 = fields.Field(column_name='Wireless 9.4')

    ContactName10 = fields.Field(column_name='Contact Name 10')
    email10 = fields.Field(column_name='Email 10')
    landline10_1 = fields.Field(column_name='Landline 10.1')
    landline10_2 = fields.Field(column_name='Landline 10.2')
    landline10_3 = fields.Field(column_name='Landline 10.3')
    landline10_4 = fields.Field(column_name='Landline 10.4')
    wireless10_1 = fields.Field(column_name='Wireless 10.1')
    wireless10_2 = fields.Field(column_name='Wireless 10.2')
    wireless10_3 = fields.Field(column_name='Wireless 10.3')
    wireless10_4 = fields.Field(column_name='Wireless 10.4')

    ContactName11 = fields.Field(column_name='Contact Name 11')
    email11 = fields.Field(column_name='Email 11')
    landline11_1 = fields.Field(column_name='Landline 11.1')
    landline11_2 = fields.Field(column_name='Landline 11.2')
    landline11_3 = fields.Field(column_name='Landline 11.3')
    landline11_4 = fields.Field(column_name='Landline 11.4')
    wireless11_1 = fields.Field(column_name='Wireless 11.1')
    wireless11_2 = fields.Field(column_name='Wireless 11.2')
    wireless11_3 = fields.Field(column_name='Wireless 11.3')
    wireless11_4 = fields.Field(column_name='Wireless 11.4')

    ContactName12 = fields.Field(column_name='Contact Name 12')
    email12 = fields.Field(column_name='Email 12')
    landline12_1 = fields.Field(column_name='Landline 12.1')
    landline12_2 = fields.Field(column_name='Landline 12.2')
    landline12_3 = fields.Field(column_name='Landline 12.3')
    landline12_4 = fields.Field(column_name='Landline 12.4')
    wireless12_1 = fields.Field(column_name='Wireless 12.1')
    wireless12_2 = fields.Field(column_name='Wireless 12.2')
    wireless12_3 = fields.Field(column_name='Wireless 12.3')
    wireless12_4 = fields.Field(column_name='Wireless 12.4')

#Helper Function to generate fields
    def get_contact_name(self, obj):
        contacts = []
        emails = []
        wireless1 = []
        wireless2 = []
        wireless3 = []
        wireless4 = []
        landline1 = []
        landline2 = []
        landline3 = []
        landline4 = []
        for defendant in obj.defendant.all():
            if defendant.business_name == "":
                ContactName = f"{defendant.name_prefix} {defendant.first_name} {defendant.middle_name} {defendant.last_name} {defendant.name_suffix}".strip()
            else:
                ContactName = f"{defendant.business_name} ({defendant.designation} : {defendant.name_prefix} {defendant.first_name} {defendant.middle_name} {defendant.last_name} {defendant.name_suffix})".strip()
            if ContactName not in contacts:
                if len(defendant.emails.all()) > 0:
                    allemail = ", ".join(email.email_address for email in defendant.emails.all())
                else:
                    allemail = "-"
                contacts.append(ContactName)
                emails.append(allemail)
                wirelessList = defendant.wireless.all()
                wireless1.append(wirelessList[0].w_number if len(wirelessList) > 0 else '-')
                wireless2.append(wirelessList[1].w_number if len(wirelessList) > 1 else '-')
                wireless3.append(wirelessList[2].w_number if len(wirelessList) > 2 else '-')
                wireless4.append(wirelessList[3].w_number if len(wirelessList) > 3 else '-')
                landlineList = defendant.landline.all()
                landline1.append(landlineList[0].l_number if len(landlineList) > 0 else '-')
                landline2.append(landlineList[1].l_number if len(landlineList) > 1 else '-')
                landline3.append(landlineList[2].l_number if len(landlineList) > 2 else '-')
                landline4.append(landlineList[3].l_number if len(landlineList) > 3 else '-')
                
            for contact in defendant.related_contacts.all():
                if contact.business_name == "":
                    ContactName = f"{contact.name_prefix} {contact.first_name} {contact.middle_name} {contact.last_name} {contact.name_suffix}".strip()
                else:
                    ContactName = f"{contact.business_name} ({contact.designation} : {contact.name_prefix} {contact.first_name} {contact.middle_name} {contact.last_name} {contact.name_suffix})".strip()
                if ContactName not in contacts:
                    if len(contact.emails.all()) > 0:
                        allemail = ", ".join(email.email_address for email in contact.emails.all())
                    else:
                        allemail = "-"
                    contacts.append(ContactName)
                    emails.append(allemail)
                    wirelessList = contact.wireless.all()
                    wireless1.append(wirelessList[0].w_number if len(wirelessList) > 0 else '-')
                    wireless2.append(wirelessList[1].w_number if len(wirelessList) > 1 else '-')
                    wireless3.append(wirelessList[2].w_number if len(wirelessList) > 2 else '-')
                    wireless4.append(wirelessList[3].w_number if len(wirelessList) > 3 else '-')
                    landlineList = contact.landline.all()
                    landline1.append(landlineList[0].l_number if len(landlineList) > 0 else '-')
                    landline2.append(landlineList[1].l_number if len(landlineList) > 1 else '-')
                    landline3.append(landlineList[2].l_number if len(landlineList) > 2 else '-')
                    landline4.append(landlineList[3].l_number if len(landlineList) > 3 else '-')
        return {
            "contacts": contacts,
            "emails": emails,
            "wireless1":wireless1,
            "wireless2":wireless2,
            "wireless3":wireless3,
            "wireless4":wireless4,
            "landline1":landline1,
            "landline2":landline2,
            "landline3":landline3,
            "landline4":landline4,
        }
    
# Dehydrate Contact Names
    def dehydrate_ContactName1(self, obj):
        contact_info = self.get_contact_name(obj)
        contacts = contact_info["contacts"]
        return contacts[0] if len(contacts) > 0 else "-"
    def dehydrate_ContactName2(self, obj):
        contact_info = self.get_contact_name(obj)
        contacts = contact_info["contacts"]
        return contacts[1] if len(contacts) > 1 else "-"
    def dehydrate_ContactName3(self, obj):
        contact_info = self.get_contact_name(obj)
        contacts = contact_info["contacts"]
        return contacts[2] if len(contacts) > 2 else "-"
    def dehydrate_ContactName4(self, obj):
        contact_info = self.get_contact_name(obj)
        contacts = contact_info["contacts"]
        return contacts[3] if len(contacts) > 3 else "-"
    def dehydrate_ContactName5(self, obj):
        contact_info = self.get_contact_name(obj)
        contacts = contact_info["contacts"]
        return contacts[4] if len(contacts) > 4 else "-"
    def dehydrate_ContactName6(self, obj):
        contact_info = self.get_contact_name(obj)
        contacts = contact_info["contacts"]
        return contacts[5] if len(contacts) > 5 else "-"
    def dehydrate_ContactName7(self, obj):
        contact_info = self.get_contact_name(obj)
        contacts = contact_info["contacts"]
        return contacts[6] if len(contacts) > 6 else "-"
    def dehydrate_ContactName8(self, obj):
        contact_info = self.get_contact_name(obj)
        contacts = contact_info["contacts"]
        return contacts[7] if len(contacts) > 7 else "-"
    def dehydrate_ContactName9(self, obj):
        contact_info = self.get_contact_name(obj)
        contacts = contact_info["contacts"]
        return contacts[8] if len(contacts) > 8 else "-"
    def dehydrate_ContactName10(self, obj):
        contact_info = self.get_contact_name(obj)
        contacts = contact_info["contacts"]
        return contacts[9] if len(contacts) > 9 else "-"
    def dehydrate_ContactName11(self, obj):
        contact_info = self.get_contact_name(obj)
        contacts = contact_info["contacts"]
        return contacts[10] if len(contacts) > 10 else "-"
    def dehydrate_ContactName12(self, obj):
        contact_info = self.get_contact_name(obj)
        contacts = contact_info["contacts"]
        return contacts[11] if len(contacts) > 11 else "-"
    
# Dehydrate Emails
    def dehydrate_email1(self, obj):
        contact_info = self.get_contact_name(obj)
        emails = contact_info["emails"]
        return emails[0] if len(emails) > 0 else "-"
    def dehydrate_email2(self, obj):
        contact_info = self.get_contact_name(obj)
        emails = contact_info["emails"]
        return emails[1] if len(emails) > 1 else "-"
    def dehydrate_email3(self, obj):
        contact_info = self.get_contact_name(obj)
        emails = contact_info["emails"]
        return emails[2] if len(emails) > 2 else "-"
    def dehydrate_email4(self, obj):
        contact_info = self.get_contact_name(obj)
        emails = contact_info["emails"]
        return emails[3] if len(emails) > 3 else "-"
    def dehydrate_email5(self, obj):
        contact_info = self.get_contact_name(obj)
        emails = contact_info["emails"]
        return emails[4] if len(emails) > 4 else "-"
    def dehydrate_email6(self, obj):
        contact_info = self.get_contact_name(obj)
        emails = contact_info["emails"]
        return emails[5] if len(emails) > 5 else "-"
    def dehydrate_email7(self, obj):
        contact_info = self.get_contact_name(obj)
        emails = contact_info["emails"]
        return emails[6] if len(emails) > 6 else "-"
    def dehydrate_email8(self, obj):
        contact_info = self.get_contact_name(obj)
        emails = contact_info["emails"]
        return emails[7] if len(emails) > 7 else "-"
    def dehydrate_email9(self, obj):
        contact_info = self.get_contact_name(obj)
        emails = contact_info["emails"]
        return emails[8] if len(emails) > 8 else "-"
    def dehydrate_email10(self, obj):
        contact_info = self.get_contact_name(obj)
        emails = contact_info["emails"]
        return emails[9] if len(emails) > 9 else "-"
    def dehydrate_email11(self, obj):
        contact_info = self.get_contact_name(obj)
        emails = contact_info["emails"]
        return emails[10] if len(emails) > 10 else "-"
    def dehydrate_email12(self, obj):
        contact_info = self.get_contact_name(obj)
        emails = contact_info["emails"]
        return emails[11] if len(emails) > 11 else "-"
    
#dehydrate Wirelesses
    def dehydrate_wireless1_1(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless1 = contact_info["wireless1"]
        return wireless1[0] if len(wireless1) > 0 else "-"
    def dehydrate_wireless2_1(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless1 = contact_info["wireless1"]
        return wireless1[1] if len(wireless1) > 1 else "-"
    def dehydrate_wireless3_1(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless1 = contact_info["wireless1"]
        return wireless1[2] if len(wireless1) > 2 else "-"
    def dehydrate_wireless4_1(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless1 = contact_info["wireless1"]
        return wireless1[3] if len(wireless1) > 3 else "-"
    def dehydrate_wireless5_1(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless1 = contact_info["wireless1"]
        return wireless1[4] if len(wireless1) > 4 else "-"
    def dehydrate_wireless6_1(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless1 = contact_info["wireless1"]
        return wireless1[5] if len(wireless1) > 5 else "-"
    def dehydrate_wireless7_1(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless1 = contact_info["wireless1"]
        return wireless1[6] if len(wireless1) > 6 else "-"
    def dehydrate_wireless8_1(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless1 = contact_info["wireless1"]
        return wireless1[7] if len(wireless1) > 7 else "-"
    def dehydrate_wireless9_1(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless1 = contact_info["wireless1"]
        return wireless1[8] if len(wireless1) > 8 else "-"
    def dehydrate_wireless10_1(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless1 = contact_info["wireless1"]
        return wireless1[9] if len(wireless1) > 9 else "-"
    def dehydrate_wireless11_1(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless1 = contact_info["wireless1"]
        return wireless1[10] if len(wireless1) > 10 else "-"
    def dehydrate_wireless12_1(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless1 = contact_info["wireless1"]
        return wireless1[11] if len(wireless1) > 11 else "-"
    
    def dehydrate_wireless1_2(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless2 = contact_info["wireless2"]
        return wireless2[0] if len(wireless2) > 0 else "-"
    def dehydrate_wireless2_2(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless2 = contact_info["wireless2"]
        return wireless2[1] if len(wireless2) > 1 else "-"
    def dehydrate_wireless3_2(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless2 = contact_info["wireless2"]
        return wireless2[2] if len(wireless2) > 2 else "-"
    def dehydrate_wireless4_2(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless2 = contact_info["wireless2"]
        return wireless2[3] if len(wireless2) > 3 else "-"
    def dehydrate_wireless5_2(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless2 = contact_info["wireless2"]
        return wireless2[4] if len(wireless2) > 4 else "-"
    def dehydrate_wireless6_2(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless2 = contact_info["wireless2"]
        return wireless2[5] if len(wireless2) > 5 else "-"
    def dehydrate_wireless7_2(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless2 = contact_info["wireless2"]
        return wireless2[6] if len(wireless2) > 6 else "-"
    def dehydrate_wireless8_2(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless2 = contact_info["wireless2"]
        return wireless2[7] if len(wireless2) > 7 else "-"
    def dehydrate_wireless9_2(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless2 = contact_info["wireless2"]
        return wireless2[8] if len(wireless2) > 8 else "-"
    def dehydrate_wireless10_2(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless2 = contact_info["wireless2"]
        return wireless2[9] if len(wireless2) > 9 else "-"
    def dehydrate_wireless11_2(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless2 = contact_info["wireless2"]
        return wireless2[10] if len(wireless2) > 10 else "-"
    def dehydrate_wireless12_2(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless2 = contact_info["wireless2"]
        return wireless2[11] if len(wireless2) > 11 else "-"

    def dehydrate_wireless1_3(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless3 = contact_info["wireless3"]
        return wireless3[0] if len(wireless3) > 0 else "-"
    def dehydrate_wireless2_3(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless3 = contact_info["wireless3"]
        return wireless3[1] if len(wireless3) > 1 else "-"
    def dehydrate_wireless3_3(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless3 = contact_info["wireless3"]
        return wireless3[2] if len(wireless3) > 2 else "-"
    def dehydrate_wireless4_3(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless3 = contact_info["wireless3"]
        return wireless3[3] if len(wireless3) > 3 else "-"
    def dehydrate_wireless5_3(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless3 = contact_info["wireless3"]
        return wireless3[4] if len(wireless3) > 4 else "-"
    def dehydrate_wireless6_3(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless3 = contact_info["wireless3"]
        return wireless3[5] if len(wireless3) > 5 else "-"
    def dehydrate_wireless7_3(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless3 = contact_info["wireless3"]
        return wireless3[6] if len(wireless3) > 6 else "-"
    def dehydrate_wireless8_3(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless3 = contact_info["wireless3"]
        return wireless3[7] if len(wireless3) > 7 else "-"
    def dehydrate_wireless9_3(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless3 = contact_info["wireless3"]
        return wireless3[8] if len(wireless3) > 8 else "-"
    def dehydrate_wireless10_3(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless3 = contact_info["wireless3"]
        return wireless3[9] if len(wireless3) > 9 else "-"
    def dehydrate_wireless11_3(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless3 = contact_info["wireless3"]
        return wireless3[10] if len(wireless3) > 10 else "-"
    def dehydrate_wireless12_3(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless3 = contact_info["wireless3"]
        return wireless3[11] if len(wireless3) > 11 else "-"
    
    def dehydrate_wireless1_4(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless4 = contact_info["wireless4"]
        return wireless4[0] if len(wireless4) > 0 else "-"
    def dehydrate_wireless2_4(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless4 = contact_info["wireless4"]
        return wireless4[1] if len(wireless4) > 1 else "-"
    def dehydrate_wireless3_4(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless4 = contact_info["wireless4"]
        return wireless4[2] if len(wireless4) > 2 else "-"
    def dehydrate_wireless4_4(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless4 = contact_info["wireless4"]
        return wireless4[3] if len(wireless4) > 3 else "-"
    def dehydrate_wireless5_4(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless4 = contact_info["wireless4"]
        return wireless4[4] if len(wireless4) > 4 else "-"
    def dehydrate_wireless6_4(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless4 = contact_info["wireless4"]
        return wireless4[5] if len(wireless4) > 5 else "-"
    def dehydrate_wireless7_4(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless4 = contact_info["wireless4"]
        return wireless4[6] if len(wireless4) > 6 else "-"
    def dehydrate_wireless8_4(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless4 = contact_info["wireless4"]
        return wireless4[7] if len(wireless4) > 7 else "-"
    def dehydrate_wireless9_4(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless4 = contact_info["wireless4"]
        return wireless4[8] if len(wireless4) > 8 else "-"
    def dehydrate_wireless10_4(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless4 = contact_info["wireless4"]
        return wireless4[9] if len(wireless4) > 9 else "-"
    def dehydrate_wireless11_4(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless4 = contact_info["wireless4"]
        return wireless4[10] if len(wireless4) > 10 else "-"
    def dehydrate_wireless12_4(self, obj):
        contact_info = self.get_contact_name(obj)
        wireless4 = contact_info["wireless4"]
        return wireless4[11] if len(wireless4) > 11 else "-"


#dehydrate landlines
    def dehydrate_landline1_1(self, obj):
        contact_info = self.get_contact_name(obj)
        landline1 = contact_info["landline1"]
        return landline1[0] if len(landline1) > 0 else "-"
    def dehydrate_landline2_1(self, obj):
        contact_info = self.get_contact_name(obj)
        landline1 = contact_info["landline1"]
        return landline1[1] if len(landline1) > 1 else "-"
    def dehydrate_landline3_1(self, obj):
        contact_info = self.get_contact_name(obj)
        landline1 = contact_info["landline1"]
        return landline1[2] if len(landline1) > 2 else "-"
    def dehydrate_landline4_1(self, obj):
        contact_info = self.get_contact_name(obj)
        landline1 = contact_info["landline1"]
        return landline1[3] if len(landline1) > 3 else "-"
    def dehydrate_landline5_1(self, obj):
        contact_info = self.get_contact_name(obj)
        landline1 = contact_info["landline1"]
        return landline1[4] if len(landline1) > 4 else "-"
    def dehydrate_landline6_1(self, obj):
        contact_info = self.get_contact_name(obj)
        landline1 = contact_info["landline1"]
        return landline1[5] if len(landline1) > 5 else "-"
    def dehydrate_landline7_1(self, obj):
        contact_info = self.get_contact_name(obj)
        landline1 = contact_info["landline1"]
        return landline1[6] if len(landline1) > 6 else "-"
    def dehydrate_landline8_1(self, obj):
        contact_info = self.get_contact_name(obj)
        landline1 = contact_info["landline1"]
        return landline1[7] if len(landline1) > 7 else "-"
    def dehydrate_landline9_1(self, obj):
        contact_info = self.get_contact_name(obj)
        landline1 = contact_info["landline1"]
        return landline1[8] if len(landline1) > 8 else "-"
    def dehydrate_landline10_1(self, obj):
        contact_info = self.get_contact_name(obj)
        landline1 = contact_info["landline1"]
        return landline1[9] if len(landline1) > 9 else "-"
    def dehydrate_landline11_1(self, obj):
        contact_info = self.get_contact_name(obj)
        landline1 = contact_info["landline1"]
        return landline1[10] if len(landline1) > 10 else "-"
    def dehydrate_landline12_1(self, obj):
        contact_info = self.get_contact_name(obj)
        landline1 = contact_info["landline1"]
        return landline1[11] if len(landline1) > 11 else "-"
    
    def dehydrate_landline1_2(self, obj):
        contact_info = self.get_contact_name(obj)
        landline2 = contact_info["landline2"]
        return landline2[0] if len(landline2) > 0 else "-"
    def dehydrate_landline2_2(self, obj):
        contact_info = self.get_contact_name(obj)
        landline2 = contact_info["landline2"]
        return landline2[1] if len(landline2) > 1 else "-"
    def dehydrate_landline3_2(self, obj):
        contact_info = self.get_contact_name(obj)
        landline2 = contact_info["landline2"]
        return landline2[2] if len(landline2) > 2 else "-"
    def dehydrate_landline4_2(self, obj):
        contact_info = self.get_contact_name(obj)
        landline2 = contact_info["landline2"]
        return landline2[3] if len(landline2) > 3 else "-"
    def dehydrate_landline5_2(self, obj):
        contact_info = self.get_contact_name(obj)
        landline2 = contact_info["landline2"]
        return landline2[4] if len(landline2) > 4 else "-"
    def dehydrate_landline6_2(self, obj):
        contact_info = self.get_contact_name(obj)
        landline2 = contact_info["landline2"]
        return landline2[5] if len(landline2) > 5 else "-"
    def dehydrate_landline7_2(self, obj):
        contact_info = self.get_contact_name(obj)
        landline2 = contact_info["landline2"]
        return landline2[6] if len(landline2) > 6 else "-"
    def dehydrate_landline8_2(self, obj):
        contact_info = self.get_contact_name(obj)
        landline2 = contact_info["landline2"]
        return landline2[7] if len(landline2) > 7 else "-"
    def dehydrate_landline9_2(self, obj):
        contact_info = self.get_contact_name(obj)
        landline2 = contact_info["landline2"]
        return landline2[8] if len(landline2) > 8 else "-"
    def dehydrate_landline10_2(self, obj):
        contact_info = self.get_contact_name(obj)
        landline2 = contact_info["landline2"]
        return landline2[9] if len(landline2) > 9 else "-"
    def dehydrate_landline11_2(self, obj):
        contact_info = self.get_contact_name(obj)
        landline2 = contact_info["landline2"]
        return landline2[10] if len(landline2) > 10 else "-"
    def dehydrate_landline12_2(self, obj):
        contact_info = self.get_contact_name(obj)
        landline2 = contact_info["landline2"]
        return landline2[11] if len(landline2) > 11 else "-"

    def dehydrate_landline1_3(self, obj):
        contact_info = self.get_contact_name(obj)
        landline3 = contact_info["landline3"]
        return landline3[0] if len(landline3) > 0 else "-"
    def dehydrate_landline2_3(self, obj):
        contact_info = self.get_contact_name(obj)
        landline3 = contact_info["landline3"]
        return landline3[1] if len(landline3) > 1 else "-"
    def dehydrate_landline3_3(self, obj):
        contact_info = self.get_contact_name(obj)
        landline3 = contact_info["landline3"]
        return landline3[2] if len(landline3) > 2 else "-"
    def dehydrate_landline4_3(self, obj):
        contact_info = self.get_contact_name(obj)
        landline3 = contact_info["landline3"]
        return landline3[3] if len(landline3) > 3 else "-"
    def dehydrate_landline5_3(self, obj):
        contact_info = self.get_contact_name(obj)
        landline3 = contact_info["landline3"]
        return landline3[4] if len(landline3) > 4 else "-"
    def dehydrate_landline6_3(self, obj):
        contact_info = self.get_contact_name(obj)
        landline3 = contact_info["landline3"]
        return landline3[5] if len(landline3) > 5 else "-"
    def dehydrate_landline7_3(self, obj):
        contact_info = self.get_contact_name(obj)
        landline3 = contact_info["landline3"]
        return landline3[6] if len(landline3) > 6 else "-"
    def dehydrate_landline8_3(self, obj):
        contact_info = self.get_contact_name(obj)
        landline3 = contact_info["landline3"]
        return landline3[7] if len(landline3) > 7 else "-"
    def dehydrate_landline9_3(self, obj):
        contact_info = self.get_contact_name(obj)
        landline3 = contact_info["landline3"]
        return landline3[8] if len(landline3) > 8 else "-"
    def dehydrate_landline10_3(self, obj):
        contact_info = self.get_contact_name(obj)
        landline3 = contact_info["landline3"]
        return landline3[9] if len(landline3) > 9 else "-"
    def dehydrate_landline11_3(self, obj):
        contact_info = self.get_contact_name(obj)
        landline3 = contact_info["landline3"]
        return landline3[10] if len(landline3) > 10 else "-"
    def dehydrate_landline12_3(self, obj):
        contact_info = self.get_contact_name(obj)
        landline3 = contact_info["landline3"]
        return landline3[11] if len(landline3) > 11 else "-"
    
    def dehydrate_landline1_4(self, obj):
        contact_info = self.get_contact_name(obj)
        landline4 = contact_info["landline4"]
        return landline4[0] if len(landline4) > 0 else "-"
    def dehydrate_landline2_4(self, obj):
        contact_info = self.get_contact_name(obj)
        landline4 = contact_info["landline4"]
        return landline4[1] if len(landline4) > 1 else "-"
    def dehydrate_landline3_4(self, obj):
        contact_info = self.get_contact_name(obj)
        landline4 = contact_info["landline4"]
        return landline4[2] if len(landline4) > 2 else "-"
    def dehydrate_landline4_4(self, obj):
        contact_info = self.get_contact_name(obj)
        landline4 = contact_info["landline4"]
        return landline4[3] if len(landline4) > 3 else "-"
    def dehydrate_landline5_4(self, obj):
        contact_info = self.get_contact_name(obj)
        landline4 = contact_info["landline4"]
        return landline4[4] if len(landline4) > 4 else "-"
    def dehydrate_landline6_4(self, obj):
        contact_info = self.get_contact_name(obj)
        landline4 = contact_info["landline4"]
        return landline4[5] if len(landline4) > 5 else "-"
    def dehydrate_landline7_4(self, obj):
        contact_info = self.get_contact_name(obj)
        landline4 = contact_info["landline4"]
        return landline4[6] if len(landline4) > 6 else "-"
    def dehydrate_landline8_4(self, obj):
        contact_info = self.get_contact_name(obj)
        landline4 = contact_info["landline4"]
        return landline4[7] if len(landline4) > 7 else "-"
    def dehydrate_landline9_4(self, obj):
        contact_info = self.get_contact_name(obj)
        landline4 = contact_info["landline4"]
        return landline4[8] if len(landline4) > 8 else "-"
    def dehydrate_landline10_4(self, obj):
        contact_info = self.get_contact_name(obj)
        landline4 = contact_info["landline4"]
        return landline4[9] if len(landline4) > 9 else "-"
    def dehydrate_landline11_4(self, obj):
        contact_info = self.get_contact_name(obj)
        landline4 = contact_info["landline4"]
        return landline4[10] if len(landline4) > 10 else "-"
    def dehydrate_landline12_4(self, obj):
        contact_info = self.get_contact_name(obj)
        landline4 = contact_info["landline4"]
        return landline4[11] if len(landline4) > 11 else "-"


#--------------other fields-----------------
    def dehydrate_DateListed(self, obj):
        return obj.created_at.strftime('%m/%d/%Y') if obj.created_at else ''
    def dehydrate_LastReported(self, obj):
        return obj.changed_at.strftime('%m/%d/%Y') if obj.changed_at else ''


    def dehydrate_CaseNumber(self, obj):
        return f"{obj.case_number}({obj.case_number_ext})".strip()

    def dehydrate_Plaintiff(self, obj):
        return ", ".join(
            f"{entity.business_name} | {entity.individual_name}".strip()
            for entity in obj.plaintiff.all()
        )
    def dehydrate_Defendant(self, obj):
        return ", ".join(
            f"{contact.name_prefix} {contact.first_name} {contact.middle_name} {contact.last_name} {contact.name_suffix}|{contact.business_name}".strip()
            for contact in obj.defendant.all()
        )
    def dehydrate_parcel_id(self, obj):
        return ", ".join(property.parcel for property in obj.property.all())
    
    def dehydrate_StreetAddress(self, obj):
        return ", ".join(
            f"{property.house_number} {property.road_name} {property.road_type} {property.direction} {property.apt_unit}{property.extention}".strip()
            for property in obj.property.all()
        )

    def dehydrate_City(self, obj):
        return ", ".join(property.city for property in obj.property.all())

    def dehydrate_Zip(self, obj):
        return ", ".join(property.zip_code for property in obj.property.all()
        )
#--------------other fields-----------------end

    class Meta:
        model = Foreclosure
        fields = ('state', 'county', 'DateListed', 'LastReported', 'id', 'comment', 'surplus_status', 'CaseNumber', 'sale_date', 'sale_type', 'Plaintiff', 'Defendant',  'fcl_final_judgment', 'sale_price', 'possible_surplus', 'verified_surplus', 'parcel_id', 'StreetAddress', 'City', 'Zip', 
                  'ContactName1', 'email1', 'wireless1_1', 'wireless1_2', 'wireless1_3', 'wireless1_4', 'landline1_1', 'landline1_2', 'landline1_3', 'landline1_4',
                  'ContactName2', 'email2', 'wireless2_1', 'wireless2_2', 'wireless2_3', 'wireless2_4', 'landline2_1', 'landline2_2', 'landline2_3', 'landline2_4',
                  'ContactName3', 'email3', 'wireless3_1', 'wireless3_2', 'wireless3_3', 'wireless3_4', 'landline3_1', 'landline3_2', 'landline3_3', 'landline3_4',
                  'ContactName4', 'email4', 'wireless4_1', 'wireless4_2', 'wireless4_3', 'wireless4_4', 'landline4_1', 'landline4_2', 'landline4_3', 'landline4_4',
                  'ContactName5', 'email5', 'wireless5_1', 'wireless5_2', 'wireless5_3', 'wireless5_4', 'landline5_1', 'landline5_2', 'landline5_3', 'landline5_4',
                  'ContactName6', 'email6', 'wireless6_1', 'wireless6_2', 'wireless6_3', 'wireless6_4', 'landline6_1', 'landline6_2', 'landline6_3', 'landline6_4',
                  'ContactName7', 'email7', 'wireless7_1', 'wireless7_2', 'wireless7_3', 'wireless7_4', 'landline7_1', 'landline7_2', 'landline7_3', 'landline7_4',
                  'ContactName8', 'email8', 'wireless8_1', 'wireless8_2', 'wireless8_3', 'wireless8_4', 'landline8_1', 'landline8_2', 'landline8_3', 'landline8_4',
                  'ContactName9', 'email9', 'wireless9_1', 'wireless9_2', 'wireless9_3', 'wireless9_4', 'landline9_1', 'landline9_2', 'landline9_3', 'landline9_4',
                  'ContactName10', 'email10', 'wireless10_1', 'wireless10_2', 'wireless10_3', 'wireless10_4', 'landline10_1', 'landline10_2', 'landline10_3', 'landline10_4',
                  'ContactName11', 'email11', 'wireless11_1', 'wireless11_2', 'wireless11_3', 'wireless11_4', 'landline11_1', 'landline11_2', 'landline11_3', 'landline11_4',
                  'ContactName12', 'email12', 'wireless12_1', 'wireless12_2', 'wireless12_3', 'wireless12_4', 'landline12_1', 'landline12_2', 'landline12_3', 'landline12_4',
                  )