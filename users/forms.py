from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Account

class GeneralInfo(forms.ModelForm):

    email       = forms.EmailField()
    username    = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirmation = forms.CharField(widget=forms.PasswordInput)
    phone_number        = forms.CharField(max_length=15, required=False)
    role = forms.ChoiceField(choices=[(role, label) for role, label in Account.ROLE_LIST if role != 'Administrator'])

    class Meta:
        model = Account
        fields = ['username','email','password','password_confirmation', 'phone_number', 'role']

    def clean_password_confirmation(self):
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password_confirmation')

        if password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        
        return password2

class StudentSignUp(forms.Form):
    study_program       = forms.CharField(max_length=100, required=False)
    years_of_study      = forms.IntegerField(required=False)
    gpa                 = forms.FloatField(required=False)

class FunderSignUp(forms.Form):
    organization_name   = forms.CharField(max_length=255, required=False)