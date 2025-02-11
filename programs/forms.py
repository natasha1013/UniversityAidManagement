from django import forms
from .models import AidProgram, FundUtilization

class AidProgramForm(forms.ModelForm):
    AID_TYPE_CHOICES = [
        ("Scholarship", "Scholarship"),
        ("Discount", "Discount"),
        ("Loan", "Loan"),
    ]

    aid_type = forms.ChoiceField(
        choices=AID_TYPE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    closing_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )

    class Meta:
        model = AidProgram
        fields = ["name", "owner", "aid_type", "level", "locality", "status", "eligibility", "closing_date", "required_documents", "total_funds"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "owner": forms.TextInput(attrs={"class": "form-control"}),
            "level": forms.Select(attrs={"class": "form-select"}),
            "locality": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "eligibility": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "required_documents": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "total_funds": forms.NumberInput(attrs={"class": "form-control"}),
        }

class FundUtilizationForm(forms.ModelForm):
    class Meta:
        model = FundUtilization
        fields = ['category', 'amount', 'description', 'transaction_date']
        widgets = {
            'transaction_date': forms.DateInput(attrs={'type': 'date'}),
        }
        \
