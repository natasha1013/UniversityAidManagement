from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from .forms import *
from .models import Account

@never_cache
def signup(request):

    # Redirect to dashboard if the user is already logged in
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    error_message = None
    if request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():
            # Extract cleaned data
            data = form.cleaned_data

            # Role determines additional fields
            role = data['role']
            is_approved = role not in ['officer', 'funder']  # Officers & funders need approval

            # Create user
            user = Account.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                role=role,
                phone_number=data['phone_number'],
                study_program=data.get('study_program', None),
                years_of_study=data.get('years_of_study', None),
                gpa=data.get('gpa', None),
                organization_name=data.get('organization_name', None),
                is_approved=is_approved
            )

            # Redirect based on approval status
            if role in ['officer', 'funder']:
                messages.success(request, "Your account is pending approval.")
                return redirect("approval_pending")
            else:
                messages.success(request, "Sign-up successful! You can now log in.")
                return redirect("login")

        else:
            error_message = "Error. Please check your details."

    else:
        form = SignUpForm()  # Empty form for GET request
        form.fields['role'].choices = [choice for choice in form.fields['role'].choices if choice[0] != 'administrator']

    return render(request, "users/signup.html", {"form": form, "error_message": error_message})

def approval_pending(request):
    return render(request, 'users/approval_pending.html')

@never_cache
def login(request):
    # Redirect to dashboard if the user is already logged in
    if request.user.is_authenticated:
        return redirect('dashboard')

    error_message = None  # Default no error
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Authenticate user
            user = authenticate(request, username=username, password=password)
            
            if user is not None:

                # Check if the user's account is approved
                if user.is_approved:  # Assuming `is_approved` is a boolean field in your User model
                    auth_login(request, user)
                    return redirect('dashboard')
                else:
                    # Redirect to pending approval page if account is not approved
                    return redirect('approval_pending')
            else:
                error_message = "Invalid username or password"
        else:
            error_message = "Invalid username or password"  # Error when form is not valid

    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form, 'error_message': error_message})

def home(request):
    return redirect('login')

def test(request):
    return render(request, 'users/test.html')

@login_required
def dashboard(request):
    return render(request, 'users/dashboard.html')

@login_required
def logout_view(request):
    logout(request)  # This will log out the user
    return redirect('login')  # Redirect to the login page