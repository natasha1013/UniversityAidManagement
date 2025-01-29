from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import Account

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirmation = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=[(role, label) for role, label in Account.ROLE_LIST if role != 'Administrator'])

    # Common fields (we won't render them directly)
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'role-username'}))
    phone_number = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'role-phone'}))

    # Student-specific fields
    study_program = forms.CharField(max_length=100, required=False)
    years_of_study = forms.IntegerField(required=False)
    gpa = forms.FloatField(required=False)

    # Funder-specific fields
    organization_name = forms.CharField(max_length=255, required=False)

    class Meta:
        model = Account
        fields = [
            'email', 'password', 'password_confirmation', 'role',
            'username', 'phone_number', 'study_program', 'years_of_study',
            'gpa', 'organization_name'
        ]

    def clean_password_confirmation(self):
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password_confirmation')

        if password1 != password2:
            raise forms.ValidationError("Passwords don't match")

        return password2
    
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)

            if user is None:
                raise forms.ValidationError("Invalid username or password")

        return cleaned_data