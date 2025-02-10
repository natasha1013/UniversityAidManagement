from django import forms
from .models import AidProgram

class AidProgramForm(forms.ModelForm):
    class Meta:
        model = AidProgram
        fields = ["name", "owner", "aid_type", "level", "locality", "status", "eligibility", "closing_date", "required_documents", "total_funds"]