from django import forms
from .models import ScheduledEmail

class ScheduledEmailForm(forms.ModelForm):
    class Meta:
        model = ScheduledEmail
        fields = [
            "sender", "scope", "recipient", "recipients_list", "contact_list",
            "template", "custom_subject", "custom_body", "send_time"
        ]

    def clean(self):
        cleaned = super().clean()
        scope = cleaned.get("scope")
        recipient = cleaned.get("recipient")
        recipients_list = cleaned.get("recipients_list")
        contact_list = cleaned.get("contact_list")

        if scope == "single" and not recipient:
            raise forms.ValidationError("Recipient email is required for single mode.")
        if scope == "multiple" and not (recipients_list or contact_list):
            raise forms.ValidationError("Provide either contacts list or multiple emails.")
        return cleaned
