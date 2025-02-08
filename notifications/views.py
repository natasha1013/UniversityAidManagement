import csv
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from .models import Notification, SystemLog


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications/list.html', {'notifications': notifications})

@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.read = True
    notification.save()

    return redirect('/profile/?tab=notification') # Redirect to the notifications list page

@staff_member_required
def system_log_view(request):
    """
    Displays the admin log with filtering, searching, and CSV export capabilities.
    """
    # Get all logs initially
    logs = SystemLog.objects.all().order_by('-timestamp')

    # Filtering by action type
    action_type = request.GET.get('action_type', None)
    if action_type:
        logs = logs.filter(action_type=action_type)

    # Searching by description or username
    search_query = request.GET.get('search', '').strip()  # Use an empty string as default
    if search_query:
        logs = logs.filter(
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
        for log in logs:
            writer.writerow([
                log.get_action_type_display(),
                log.description,
                log.user.username if log.user else 'N/A',
                log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            ])

        return response  # Return the CSV file as a downloadable response

    # Pass action types for the dropdown
    action_types = SystemLog.ACTION_TYPES

    return render(request, 'systemlogs/system_log.html', {
        'logs': logs,
        'action_types': action_types,
        'selected_action_type': action_type,
        'search_query': search_query,
    })