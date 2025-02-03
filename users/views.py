from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.decorators.cache import never_cache
from django.contrib import messages
from .forms import *
from .models import Account

def role_required(role_name):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.role != role_name:
                raise PermissionDenied("You do not have permission to access this page.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

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

@login_required
def dashboard(request):
        # Map roles to their respective dashboard functions
    role_dashboard_map = {
        'administrator': admin_dashboard,
        'student': student_dashboard,
        'officer': officer_dashboard,
        'funder': funder_dashboard,
    }

    # Get the user's role
    user_role = request.user.role

    # Check if the role exists in the map
    if user_role in role_dashboard_map:
        # Call the appropriate dashboard function
        return role_dashboard_map[user_role](request)
    else:
        # Handle unknown roles (e.g., redirect to a default page)
        messages.error(request, "Your role is not recognized. Please contact support.")
        return redirect('home')  # Redirect to a safe fallback page

@role_required('funder')
@login_required
def funder_dashboard(request):
    return render(request, 'dashboards/funder_dashboard.html')

# admin-only views
@role_required('administrator')
@login_required
def admin_dashboard(request):
    # Get the 'tab' query parameter (default to 'pending_users')
    active_tab = request.GET.get('tab', 'pending_users')

    # Ensure the user has administrator privileges
    if request.user.role != 'administrator':
        raise PermissionDenied("You do not have permission to access this page.")

    # Fetch data based on the active tab
    context = {'active_tab': active_tab}
    if active_tab == 'pending_users':
        pending_users = Account.objects.filter(is_approved=False)
        context['pending_users'] = pending_users
    elif active_tab == 'update_user':
        users = Account.objects.all()
        context['users'] = users
    elif active_tab == 'manage_profile':
        # Add logic for managing profiles if needed
        pass

    return render(request, 'dashboards/admin_dashboard.html', context)

@login_required
def pending_users(request):
    if request.user.role != 'administrator':
        raise PermissionDenied("You do not have permission to access this page.")
    pending_users = Account.objects.filter(is_approved=False)
    return render(request, 'dashboards/admin_dashboard.html', {
        'section': 'pending_users',
        'pending_users': pending_users
    })

@login_required
def approve_user(request, user_id):
    if request.user.role != 'administrator':
        raise PermissionDenied("You do not have permission to access this page.")
    user = get_object_or_404(Account, id=user_id)
    user.is_approved = True
    user.save()
    return redirect('pending_users')

@login_required
def reject_user(request, user_id):
    if request.user.role != 'administrator':
        raise PermissionDenied("You do not have permission to access this page.")
    
    # Get the user to reject
    user = get_object_or_404(Account, id=user_id)
    
    # Delete the user account
    username = user.username  # Store the username for feedback
    user.delete()
    
    # Provide feedback to the administrator
    messages.success(request, f'User "{username}" has been rejected and removed from the system.')
    
    # Redirect back to the pending users page
    return redirect('pending_users')

@login_required
def update_user(request):
    # Example: Fetch all users for updating
    users = Account.objects.all()
    return render(request, 'dashboards/admin_dashboard.html', {'users': users, 'section': 'update_user'})

@login_required
def config_parameters(request):
    # Example: Fetch configuration parameters
    return render(request, 'dashboards/admin_dashboard.html', {'section': 'config_parameters'})

@login_required
def add_parameters(request):
    # Example: Add new parameters
    return render(request, 'dashboards/admin_dashboard.html', {'section': 'add_parameters'})

@login_required
def feedback_management(request):
    # Example: Manage feedback
    return render(request, 'dashboards/admin_dashboard.html', {'section': 'feedback_management'})

@login_required
def approve_requests(request):
    # Example: Approve fund requests
    return render(request, 'dashboards/admin_dashboard.html', {'section': 'approve_requests'})

@login_required
def edit_program(request):
    # Example: Edit program details
    return render(request, 'dashboards/admin_dashboard.html', {'section': 'edit_program'})

# officer-only views
@role_required('officer')
@login_required
def officer_dashboard(request):
    return render(request, 'dashboards/officer_dashboard.html')

@role_required('student')
@login_required
def student_dashboard(request):
    return render(request, 'dashboards/dashboard.html')

# logout 
@login_required
def logout_view(request):
    logout(request)  # This will log out the user
    return redirect('login')  # Redirect to the login page

def home(request):
    return redirect('login')

def test(request):
    return render(request, 'users/test.html')

def approval_pending(request):
    return render(request, 'users/approval_pending.html')