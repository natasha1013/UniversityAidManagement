import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.views import View
from django.views.decorators.cache import never_cache
from django.contrib import messages
from programs.models import *
from chats.models import Chat
from .forms import *
from django.db.models import Q
from .models import Account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from feedbacks.models import Feedback
from notifications.models import Notification, SystemLog
from programs.forms import AidProgramForm  # Import the AidProgramForm


## Navigations
NAVBAR_CONTENT = {
    'administrator': {
        'account': [
            {'name': 'Approve User', 'tab': 'pending_users'},
            {'name': 'Update User', 'tab': 'update_user'},
        ],
        'profile': [
            {'name': 'Edit Profile', 'tab': 'my_profile'},
        ],
        'system_settings': [
            {'name': 'System Logs', 'tab': 'system_log'},
        ],
        'communication': [
            {'name': 'Notification', 'tab': 'notification'},
            {'name': 'Chat', 'tab': 'chat'},
            {'name': 'Feedback', 'tab': 'feedback'},
        ],
        'fund_proposal': [
            {'name': 'Fund Proposal', 'tab': 'approve_requests'},
            {'name': 'Fund List', 'tab': 'edit_program'},
        ],
    },
    'student': {
        'AidPrograms': [
            {'name': 'Financial Aid', 'tab': 'financial_aid'},
            {'name': 'Application Status', 'tab': 'application_status'},
        ],

        'communication': [
            {'name': 'Notification', 'tab': 'notification'},
            {'name': 'Chat', 'tab': 'chat'},
            {'name': 'Feedback', 'tab': 'feedback'},
        ],

        'funds': [
            {'name': 'Fund Utilization', 'tab': 'fund_utilization'},
            {'name': 'Impact Report', 'tab': 'impact_report'},
        ],

        'profile': [
            {'name': 'My Profile', 'tab': 'my_profile'},
        ],
    },
    'officer': {
        'communication': [
            {'name': 'Notification', 'tab': 'notification'},
            {'name': 'Chat', 'tab': 'chat'},
            {'name': 'Feedback', 'tab': 'feedback'},
        ],

        'funds': [
            {'name': 'Aid Requests', 'tab': 'aid_request'},
            {'name': 'Fund Utilization', 'tab': 'fund_utilization'},
            {'name': 'Aid Applications', 'tab': 'aid_application'},
            {'name': 'Impact Report', 'tab': 'impact_report'},
        ],

        'profile': [
            {'name': 'My Profile', 'tab': 'my_profile'},
        ],

    },
    'funder': {
        'profile': [
            {'name': 'Edit Profile', 'tab': 'my_profile'},
        ],

        'communication': [
            {'name': 'Notification', 'tab': 'notification'},
            {'name': 'Chat', 'tab': 'chat'},
            {'name': 'Feedback', 'tab': 'feedback'},
        ],

        'fund_programs': [
            {'name': 'Fund Proposal Status', 'tab': 'status'},
            {'name': 'Submit Fund Proposal', 'tab': 'fund_proposal'},
        ],

        'fund_disbursements': [
            {'name': 'Aid Application', 'tab': 'aid_application'},
            {'name': 'Fund Utilization', 'tab': 'fund_utilization'},
            {'name': 'Impact Report', 'tab': 'impact_report'},
        ],
    },
}

## settings
def role_required(role_name):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.role != role_name:
                raise PermissionDenied("You do not have permission to access this page.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

@csrf_exempt
def user_detail_api(request, user_id):
    try:
        user = Account.objects.get(id=user_id)
        data = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone_number': user.phone_number,
            'role': user.role,
        }
        if user.role == 'student':
            data.update({
                'study_program': user.study_program,
                'years_of_study': user.years_of_study,
                'gpa': user.gpa,
            })
        elif user.role == 'funder':
            data.update({
                'organization_name': user.organization_name,
            })
        return JsonResponse(data)
    except Account.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

## helpers
def get_navbar_content(user_role, active_menu):
    return NAVBAR_CONTENT.get(user_role, {}).get(active_menu, [])

def get_feedback_list(user):
    feedback_entries = Feedback.objects.filter(
        Q(sender=user) | Q(receiver=user)
    ).order_by('-created_at')
    return [
        {'feedback': feedback, 'type': 'Sent' if feedback.sender == user else 'Received'}
        for feedback in feedback_entries
    ]

def get_notifications_list(user):
    return Notification.objects.filter(user=user).order_by('-created_at')

def get_chat_users(user):
    previous_chats = Chat.objects.filter(Q(sender=user) | Q(recipient=user))
    user_ids = {chat.sender.id for chat in previous_chats} | {chat.recipient.id for chat in previous_chats}
    user_ids.discard(user.id)
    return Account.objects.filter(id__in=user_ids)

def get_active_menu(active_tab, role):
    role_menus = {
        'administrator': {
            'pending_users': 'account',
            'update_user': 'account',
            'system_log': 'system_settings',
            'notification': 'communication',
            'chat': 'communication',
            'feedback': 'communication',
            'approve_requests': 'fund_proposal',
            'edit_program': 'fund_proposal',
            'my_profile': 'profile',
        },
        'student': {
            'financial_aid': 'AidPrograms',
            'application_status': 'AidPrograms',
            'notification': 'communication',
            'chat': 'communication',
            'feedback': 'communication',
            'fund_utilization': 'funds',
            'impact_report': 'funds',
            'my_profile': 'profile',
        },
        'officer': {
            'notification': 'communication',
            'chat': 'communication',
            'feedback': 'communication',
            'aid_request': 'funds',
            'fund_utilization': 'funds',
            'aid_application': 'funds',
            'impact_report': 'funds',
            'my_profile': 'profile',
        },
        'funder': {
            'status': 'fund_programs',
            'fund_proposal': 'fund_programs',
            'notification': 'communication',
            'chat': 'communication',
            'feedback': 'communication',
            'aid_application': 'fund_disbursements',
            'fund_utilization': 'fund_disbursements',
            'impact_report': 'fund_disbursements',
            'my_profile': 'profile',
        },
    }
    return role_menus.get(role, {}).get(active_tab, 'default_menu')

def get_aids_list():
    """
    Returns all aid programs from the database.
    """
    return AidProgram.objects.all()

def get_application_statuses(user):
    """
    Returns application statuses based on the user's role:
    - Students can view only their own applications.
    - Aid officers can view all applications.
    """
    # Check if the user is a student or an aid officer
    if user.role == 'student':
        # Students can only see their own applications
        return ApplicationStatus.objects.filter(student=user)
    elif user.role == 'officer':
        # Aid officers can see all applications
        return ApplicationStatus.objects.all()
    else:
        # Raise an error for unsupported roles
        raise PermissionDenied("You do not have permission to view application statuses.")

def filter_system_logs(queryset, action_type=None, search_query=None):
    if action_type:
        queryset = queryset.filter(action_type=action_type)
    if search_query:
        queryset = queryset.filter(
            Q(description__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    return queryset.order_by('-timestamp')

def export_to_csv(queryset, filename, headers, row_generator):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(headers)
    for item in queryset:
        writer.writerow(row_generator(item))
    return response

## authentications
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
                if user.is_approved: 
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
def logout_view(request):
    logout(request)  # This will log out the user
    return redirect('login')  # Redirect to the login page

@login_required
def delete_account(request):
    if request.method == 'POST':
        form = ConfirmPasswordForm(request.POST, user=request.user)
        if form.is_valid():
            
           # Optionally delete related objects if any
            try:
                # If you have related models, you can delete them here
                if hasattr(request.user, 'profile'):
                    request.user.profile.delete()  # Example: Delete related profile
                # Add other related object deletions here if needed

                # Delete the user account
                user = request.user
                user.delete()

                # Log out the user
                logout(request)

                # Provide feedback to the user
                messages.success(request, 'Your account has been successfully deleted.')
                return redirect('login')

            except Exception as e:
                messages.error(request, f"Error deleting account: {e}")
                return redirect('dashboard')
    else:
        form = ConfirmPasswordForm(user=request.user)

    return render(request, 'dashboards/dashboard.html', {'form': form})


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
    return redirect(f"{reverse('dashboard')}?tab=pending_users")

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
    referer = request.META.get('HTTP_REFERER', None)  # Get the referer URL
    if referer and 'tab=pending_users' in referer:
        # Redirect back to the pending users tab
        return redirect(f"{reverse('dashboard')}?tab=pending_users")
    elif referer and 'tab=update_user' in referer:
        # Redirect back to the update user tab
        return redirect(f"{reverse('dashboard')}?tab=update_user")
    else:
        # Default fallback: redirect to the dashboard with the pending_users tab
        return redirect(f"{reverse('dashboard')}?tab=pending_users")

@login_required
def update_user(request, user_id):
    user = get_object_or_404(Account, id=user_id)

    if request.method == 'POST':
        # Common fields
        user.username = request.POST.get('username')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone_number')

        # Role-specific fields
        if user.role == 'student':
            user.study_program = request.POST.get('study_program')
            user.years_of_study = request.POST.get('years_of_study')
            user.gpa = request.POST.get('gpa')
        elif user.role == 'funder':
            user.organization_name = request.POST.get('organization_name')

        user.save()

        messages.success(request, f'User "{user.username}" has been updated.')

    # Redirect based on the referer or default to the update_user tab
    referer = request.META.get('HTTP_REFERER', None)
    if referer and 'tab=my_profile' in referer:
        return redirect(f"{reverse('dashboard')}?tab=my_profile")
    elif referer and 'tab=edit_profile' in referer:
        return redirect(f"{reverse('dashboard')}?tab=edit_profile")
    elif referer and 'tab=manage_profile' in referer:
        return redirect(f"{reverse('dashboard')}?tab=manage_profile")
    else:
        # Default fallback: redirect to the update_user tab
        return redirect(f"{reverse('dashboard')}?tab=update_user")

## dashboards
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
    active_tab = request.GET.get('tab', 'aid_application')

    # Handle form submission for proposing a new aid program
    if request.method == "POST" and active_tab == "fund_proposal":
        form = AidProgramForm(request.POST)
        if form.is_valid():
            aid_program = form.save(commit=False)
            aid_program.proposed_by = request.user  # Set the logged-in user as the proposer
            aid_program.save()
            messages.success(request, "Your aid program proposal has been submitted successfully!")
            return redirect(f'/profile/?tab=status')  # Redirect back to the dashboard
        else:
            # Debugging: Print form errors to the console or log them
            messages.error(request, "There was an error with your submission. Please check the form.")
    else:
        form = AidProgramForm()  # Create an empty form for GET requests

    # Determine the active menu based on the tab or other logic
    active_menu = get_active_menu(active_tab, request.user.role)

    # Fetch role-specific navbar content
    user_role = request.user.role
    navbar_content = get_navbar_content(request.user.role, active_menu)

    feedback_list = get_feedback_list(request.user)
    notifications_list = get_notifications_list(request.user)

    chat_users = []

    # Fetch chat-related data if the active tab is 'chat'
    if active_tab == 'chat':
        chat_users = get_chat_users(request.user)

    my_aids = AidProgram.objects.filter(proposed_by=request.user).order_by('-closing_date')

    # Fetch data based on the active tab
    context = {
        'active_tab': active_tab,
        'active_menu': active_menu,  # Pass the active menu to the template
        'navbar_content': navbar_content,  # Pass the navbar content
        'feedback_list' : feedback_list,
        'notifications_list': notifications_list,
        'chat_users': chat_users,
        'my_aids': my_aids,  # Add the list of aid programs to the context
        'form': form,  # Pass the form to the template
    }

    return render(request, 'dashboards/funder_dashboard.html', context)

# admin-only views
@role_required('administrator')
@login_required
def admin_dashboard(request):
    # Get the 'tab' query parameter (default to 'pending_users')
    active_tab = request.GET.get('tab', 'system_log')

    # Determine the active menu based on the tab or other logic
    active_menu = get_active_menu(active_tab, request.user.role)

    # Fetch role-specific navbar content
    user_role = request.user.role
    navbar_content = get_navbar_content(request.user.role, active_menu)

    feedback_list = get_feedback_list(request.user)
    notifications_list = get_notifications_list(request.user)

    # System Log Filtering
    action_type = request.GET.get('action_type')  # Define action_type explicitly
    search_query = request.GET.get('search', '').strip()  # Define search_query explicitly
    
    # System Log Filtering
    system_logs = filter_system_logs(
        SystemLog.objects.all(),
        action_type=request.GET.get('action_type'),
        search_query=request.GET.get('search', '').strip()
    )

    if request.GET.get('export') == 'csv':
        return export_to_csv(
            system_logs,
            "system_logs.csv",
            ['Action Type', 'Description', 'User', 'Timestamp'],
            lambda log: [
                log.get_action_type_display(),
                log.description,
                log.user.username if log.user else 'N/A',
                log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            ]
        )
    
    # Pass action types for the dropdown
    action_types = SystemLog.ACTION_TYPES

    chat_users = []

    # Fetch chat-related data if the active tab is 'chat'
    if active_tab == 'chat':
        chat_users = get_chat_users(request.user)

    pending_aids = AidProgram.objects.filter(approval_status='PENDING').order_by('-closing_date')

    aids_list = get_aids_list()

    # Fetch data based on the active tab
    context = {
        'active_tab': active_tab,
        'active_menu': active_menu,  # Pass the active menu to the template
        'navbar_content': navbar_content,  # Pass the navbar content
        'feedback_list' : feedback_list,
        'notifications_list': notifications_list,
        'systemLog_list' : system_logs,
        'action_types': action_types,  # Pass action types for the dropdown
        'selected_action_type': action_type,  # Pass the selected action type
        'search_query': search_query,  # Pass the search query
        'chat_users': chat_users,
        'pending_aids': pending_aids,
        'aids_list': aids_list,  # Add the list of aid programs to the context
    }

    

    if active_tab == 'pending_users':
        context['pending_users'] = Account.objects.filter(is_approved=False)
    elif active_tab == 'update_user':
        context['users'] = Account.objects.all()

    return render(request, 'dashboards/admin_dashboard.html', context)

# officer-only views
@role_required('officer')
@login_required
def officer_dashboard(request):
    active_tab = request.GET.get('tab', 'notification')

    # Determine the active menu based on the tab or other logic
    active_menu = get_active_menu(active_tab, request.user.role)

    # Fetch role-specific navbar content
    user_role = request.user.role
    navbar_content = get_navbar_content(request.user.role, active_menu)

    feedback_list = get_feedback_list(request.user)
    notifications_list = get_notifications_list(request.user)

    chat_users = []

    # Fetch chat-related data if the active tab is 'chat'
    if active_tab == 'chat':
        chat_users = get_chat_users(request.user)

    application_statuses = get_application_statuses(request.user)

    # Fetch data based on the active tab
    context = {
        'active_tab': active_tab,
        'active_menu': active_menu,  # Pass the active menu to the template
        'navbar_content': navbar_content,  # Pass the navbar content
        'feedback_list' : feedback_list,
        'notifications_list': notifications_list,
        'chat_users': chat_users,
        'application_statuses': application_statuses,  # Add application statuses to the context
    }

    return render(request, 'dashboards/officer_dashboard.html', context)

@role_required('student')
@login_required
def student_dashboard(request):
    active_tab = request.GET.get('tab', 'financial_aid')

    # Determine the active menu based on the tab or other logic
    active_menu = get_active_menu(active_tab, request.user.role)

    # Fetch role-specific navbar content
    user_role = request.user.role
    navbar_content = get_navbar_content(request.user.role, active_menu)

    feedback_list = get_feedback_list(request.user)
    notifications_list = get_notifications_list(request.user)

    chat_users = []

    # Fetch chat-related data if the active tab is 'chat'
    if active_tab == 'chat':
        chat_users = get_chat_users(request.user)
    
    aids_list = get_aids_list()
    application_statuses = get_application_statuses(request.user)

    # Fetch data based on the active tab
    context = {
        'active_tab': active_tab,
        'active_menu': active_menu,  # Pass the active menu to the template
        'navbar_content': navbar_content,  # Pass the navbar content
        'feedback_list' : feedback_list,
        'notifications_list': notifications_list,
        'chat_users': chat_users,  # Pass the list of chat users to the template
        'aids_list': aids_list,  # Add the list of aid programs to the context
        'application_statuses': application_statuses,  # Add application statuses to the context
    }

    if active_tab == 'my_profile':
        # Fetch the logged-in user's data
        logged_in_user = request.user  # Get the currently logged-in user
        context['user_profile'] = logged_in_user  # Pass the user's profile to the template

    return render(request, 'dashboards/dashboard.html', context)

## others
def home(request):
    return redirect('login')

def test(request):
    return render(request, 'users/test.html')

def approval_pending(request):
    return render(request, 'users/approval_pending.html')