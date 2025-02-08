import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.contrib import messages

from chats.models import Chat
from .forms import *
from django.db.models import Q
from .models import Account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from feedbacks.models import Feedback
from notifications.models import Notification, SystemLog


# Navbar content for each menu item, with role-based customization
NAVBAR_CONTENT = {
    'administrator': {
        'user_management': [
            {'name': 'Approve User', 'tab': 'pending_users'},
            {'name': 'Update User', 'tab': 'update_user'},
            {'name': 'Manage Profile', 'tab': 'manage_profile'},
        ],
        'system_settings': [
            {'name': 'Configuration Parameters', 'tab': 'config_parameters'},
            {'name': 'Add Parameters', 'tab': 'add_parameters'},
            {'name': 'Notification', 'tab': 'notification'},
            {'name': 'Chat', 'tab': 'chat'},
        ],
        'feedback': [
            {'name': 'Feedback Management', 'tab': 'feedback_management'},
        ],
        'fund_proposal': [
            {'name': 'Fund Proposal', 'tab': 'approve_requests'},
            {'name': 'Fund List', 'tab': 'edit_program'},
        ],
    },
    'student': {
        'homepage': [
            {'name': 'Financial Aid', 'tab': 'financial_aid'},
            {'name': 'Notification', 'tab': 'notification'},
            {'name': 'Chat', 'tab': 'chat'},
        ],

        'profile': [
            {'name': 'My Profile', 'tab': 'my_profile'},
            {'name': 'Application Status', 'tab': 'application_status'},
            {'name': 'Fund Utilization', 'tab': 'fund_utilization'},
            {'name': 'Feedback', 'tab': 'feedback'},
        ],
    },
    'officer': {
        'communication': [
            {'name': 'Chat', 'tab': 'chat'},
            {'name': 'Feedback', 'tab': 'feedback'},
            {'name': 'Notification', 'tab': 'notification'},
        ],

        'fund_utilizations': [
            {'name': 'Fund Utilization', 'tab': 'fund_utilization'},
        ],

        'aid_applications': [
            {'name': 'Aid Applications', 'tab': 'aid_application'},
            {'name': 'Aid Requests', 'tab': 'aid_request'},
        ],

        'report': [
            {'name': 'Impact Report', 'tab': 'impact_report'},
        ],

    },
    'funder': {
        'manage_profile': [
            {'name': 'Manage Profile', 'tab': 'edit_profile'},
            {'name': 'Chat', 'tab': 'chat'},
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
    active_tab = request.GET.get('tab', 'edit_profile')

    # Determine the active menu based on the tab or other logic
    active_menu = 'manage_profile'  # Default menu for administrators
    if active_tab in ['status', 'fund_proposal']:
        active_menu = 'fund_programs'
    elif active_tab in ['aid_application', 'fund_utilization', 'impact_report']:
        active_menu = 'fund_disbursements'

    # Fetch role-specific navbar content
    user_role = request.user.role
    navbar_content = NAVBAR_CONTENT.get(user_role, {}).get(active_menu, [])

    chat_users = []

    # Fetch chat-related data if the active tab is 'chat'
    if active_tab == 'chat':
        # Get all users with whom the logged-in user has exchanged messages
        previous_chats = Chat.objects.filter(Q(sender=request.user) | Q(recipient=request.user))
        user_ids = set()
        for chat in previous_chats:
            user_ids.add(chat.sender.id)
            user_ids.add(chat.recipient.id)

        # Remove the current user from the list
        user_ids.discard(request.user.id)

        # Fetch the corresponding user objects
        chat_users = Account.objects.filter(id__in=user_ids)

    # Fetch data based on the active tab
    context = {
        'active_tab': active_tab,
        'active_menu': active_menu,  # Pass the active menu to the template
        'navbar_content': navbar_content,  # Pass the navbar content
        'chat_users': chat_users,
    }

    return render(request, 'dashboards/funder_dashboard.html', context)

# admin-only views
@role_required('administrator')
@login_required
def admin_dashboard(request):
    # Get the 'tab' query parameter (default to 'pending_users')
    active_tab = request.GET.get('tab', 'pending_users')

    # Determine the active menu based on the tab or other logic
    active_menu = 'user_management'  # Default menu for administrators
    if active_tab in ['config_parameters', 'add_parameters', 'notification', 'chat']:
        active_menu = 'system_settings'
    elif active_tab == 'feedback_management':
        active_menu = 'feedback'
    elif active_tab in ['approve_requests', 'edit_program']:
        active_menu = 'fund_proposal'

    # Fetch role-specific navbar content
    user_role = request.user.role
    navbar_content = NAVBAR_CONTENT.get(user_role, {}).get(active_menu, [])

    feedback_entries = Feedback.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by('-created_at')

    feedback_list = [
        {'feedback': feedback, 'type': 'Sent' if feedback.sender == request.user else 'Received'}
        for feedback in feedback_entries
    ]

    notifications_list = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # System Log Filtering
    system_logs = SystemLog.objects.all().order_by('-timestamp')  # Start with all logs

    # Filter by action type
    action_type = request.GET.get('action_type', None)
    if action_type:
        system_logs = system_logs.filter(action_type=action_type)

    # Search by description or username
    search_query = request.GET.get('search', '').strip()
    if search_query:
        system_logs = system_logs.filter(
            Q(description__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )

    if request.GET.get('export') == 'csv':
        # Create the HttpResponse object with CSV headers
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="system_logs.csv"'

        # Write the CSV data
        writer = csv.writer(response)
        writer.writerow(['Action Type', 'Description', 'User', 'Timestamp'])  # Header row
        for log in system_logs:
            writer.writerow([
                log.get_action_type_display(),
                log.description,
                log.user.username if log.user else 'N/A',
                log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            ])

        return response  # Return the CSV file as a downloadable response
    
    # Pass action types for the dropdown
    action_types = SystemLog.ACTION_TYPES

    chat_users = []

    # Fetch chat-related data if the active tab is 'chat'
    if active_tab == 'chat':
        # Get all users with whom the logged-in user has exchanged messages
        previous_chats = Chat.objects.filter(Q(sender=request.user) | Q(recipient=request.user))
        user_ids = set()
        for chat in previous_chats:
            user_ids.add(chat.sender.id)
            user_ids.add(chat.recipient.id)

        # Remove the current user from the list
        user_ids.discard(request.user.id)

        # Fetch the corresponding user objects
        chat_users = Account.objects.filter(id__in=user_ids)

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
    }

    

    if active_tab == 'pending_users':
        context['pending_users'] = Account.objects.filter(is_approved=False)
    elif active_tab == 'update_user':
        context['users'] = Account.objects.all()
    elif active_tab == 'manage_profile':
        # Not yet implemented
        pass
    elif active_tab == 'feedback_management':
        # context['feedback_list'] = feedback_list  # Fetch all feedback entries
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

    # return redirect(f"{reverse('dashboard')}?tab=update_user")
    referer = request.META.get('HTTP_REFERER', None)  # Get the referer URL
    if referer and 'tab=my_profile' in referer:
        # Redirect back to the pending users tab
        return redirect(f"{reverse('dashboard')}?tab=my_profile")
    elif referer and 'tab=update_user' in referer:
        # Redirect back to the update user tab
        return redirect(f"{reverse('dashboard')}?tab=update_user")
    elif referer and 'tab=edit_profile' in referer:
        return redirect(f"{reverse('dashboard')}?tab=edit_profile")
    
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
    active_tab = request.GET.get('tab', 'chat')

    # Determine the active menu based on the tab or other logic
    active_menu = 'communication'
    if active_tab in ['chat', 'feedback', 'notification']:
        active_menu = 'communication'
    elif active_tab in ['fund_utilization']:
        active_menu = 'fund_utilizations'
    elif active_tab in ['aid_application', 'aid_request']:
        active_menu = 'aid_applications'
    elif active_tab in ['impact_report']:
        active_menu = 'report'

    # Fetch role-specific navbar content
    user_role = request.user.role
    navbar_content = NAVBAR_CONTENT.get(user_role, {}).get(active_menu, [])

    feedback_entries = Feedback.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by('-created_at')

    feedback_list = [
        {'feedback': feedback, 'type': 'Sent' if feedback.sender == request.user else 'Received'}
        for feedback in feedback_entries
    ]

    notifications_list = Notification.objects.filter(user=request.user).order_by('-created_at')

    chat_users = []

    # Fetch chat-related data if the active tab is 'chat'
    if active_tab == 'chat':
        # Get all users with whom the logged-in user has exchanged messages
        previous_chats = Chat.objects.filter(Q(sender=request.user) | Q(recipient=request.user))
        user_ids = set()
        for chat in previous_chats:
            user_ids.add(chat.sender.id)
            user_ids.add(chat.recipient.id)

        # Remove the current user from the list
        user_ids.discard(request.user.id)

        # Fetch the corresponding user objects
        chat_users = Account.objects.filter(id__in=user_ids)

    # Fetch data based on the active tab
    context = {
        'active_tab': active_tab,
        'active_menu': active_menu,  # Pass the active menu to the template
        'navbar_content': navbar_content,  # Pass the navbar content
        'feedback_list' : feedback_list,
        'notifications_list': notifications_list,
        'chat_users': chat_users,
    }

    return render(request, 'dashboards/officer_dashboard.html', context)

@role_required('student')
@login_required
def student_dashboard(request):
    active_tab = request.GET.get('tab', 'financial_aid')

    # Determine the active menu based on the tab or other logic
    active_menu = 'homepage'
    if active_tab in ['financial_aid', 'notification', 'chat']:
        active_menu = 'homepage'
    elif active_tab in ['my_profile', 'application_status', 'fund_utilization', 'feedback']:
        active_menu = 'profile'

    # Fetch role-specific navbar content
    user_role = request.user.role
    navbar_content = NAVBAR_CONTENT.get(user_role, {}).get(active_menu, [])

    feedback_entries = Feedback.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by('-created_at')

    feedback_list = [
        {'feedback': feedback, 'type': 'Sent' if feedback.sender == request.user else 'Received'}
        for feedback in feedback_entries
    ]

    notifications_list = Notification.objects.filter(user=request.user).order_by('-created_at')

    chat_users = []

    # Fetch chat-related data if the active tab is 'chat'
    if active_tab == 'chat':
        # Get all users with whom the logged-in user has exchanged messages
        previous_chats = Chat.objects.filter(Q(sender=request.user) | Q(recipient=request.user))
        user_ids = set()
        for chat in previous_chats:
            user_ids.add(chat.sender.id)
            user_ids.add(chat.recipient.id)

        # Remove the current user from the list
        user_ids.discard(request.user.id)

        # Fetch the corresponding user objects
        chat_users = Account.objects.filter(id__in=user_ids)


    # Fetch data based on the active tab
    context = {
        'active_tab': active_tab,
        'active_menu': active_menu,  # Pass the active menu to the template
        'navbar_content': navbar_content,  # Pass the navbar content
        'feedback_list' : feedback_list,
        'notifications_list': notifications_list,
        'chat_users': chat_users,  # Pass the list of chat users to the template
    }

    if active_tab == 'my_profile':
        # Fetch the logged-in user's data
        logged_in_user = request.user  # Get the currently logged-in user
        context['user_profile'] = logged_in_user  # Pass the user's profile to the template

    return render(request, 'dashboards/dashboard.html', context)

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