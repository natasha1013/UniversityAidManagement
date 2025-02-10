from django.db.models.signals import pre_save, post_save, pre_delete
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Notification, SystemLog
from users.models import Account
from feedbacks.models import Feedback
from chats.models import Chat
from programs.models import *

User = get_user_model()

# Dictionary to store old values before update
old_values = {}

@receiver(post_save, sender=User)
def send_welcome_notification(sender, instance, created, **kwargs):
    """
    Sends a welcome notification when a new user is created.
    """
    if created:
        Notification.objects.create(
            user=instance,
            message="Welcome to our platform! We're glad to have you."
        )

@receiver(pre_save, sender=Account)
def capture_old_values(sender, instance, **kwargs):
    """
    Captures old field values before saving an Account instance.
    """
    if instance.pk:  # Only capture if instance exists
        try:
            old_instance = Account.objects.get(pk=instance.pk)
            old_values[instance.pk] = {
                "first_name": old_instance.first_name,
                "last_name": old_instance.last_name,
                "phone_number": old_instance.phone_number,
                "study_program": old_instance.study_program,
                "years_of_study": old_instance.years_of_study,
                "gpa": old_instance.gpa,
                "organization_name": old_instance.organization_name,
            }
        except Account.DoesNotExist:
            pass  # If instance doesn't exist yet, do nothing

@receiver(post_save, sender=Account)
def send_profile_update_notification(sender, instance, created, **kwargs):
    """
    Sends a notification only if the profile was updated with actual changes.
    """
    if created or instance.pk not in old_values:
        return  # Skip notifications for new accounts

    old_data = old_values.pop(instance.pk, {})  # Retrieve old values and remove from storage
    changes = []

    # Helper function to safely compare values
    def safe_compare(old, new):
        """
        Compares two values safely, ignoring None vs empty strings and stripping extra spaces.
        """
        if old is None and new in [None, ""]:
            return False  # Treat None and empty as equivalent
        if isinstance(old, str) and isinstance(new, str) and old.strip() == new.strip():
            return False  # Ignore whitespace differences
        if isinstance(old, (int, float)) and isinstance(new, (int, float)):
            return float(old) != float(new)  # Convert to float to avoid mismatches
        return old != new

    # List of fields to check for changes
    fields_to_check = {
        "First Name": "first_name",
        "Last Name": "last_name",
        "Phone Number": "phone_number",
    }

    # Add role-specific fields
    if instance.role == "student":
        fields_to_check.update({
            "Study Program": "study_program",
            "Years of Study": "years_of_study",
            "GPA": "gpa",
        })
    elif instance.role == "officer":
        fields_to_check.update({
            "Organization Name": "organization_name",
        })

    # Compare each field
    for field_label, field_name in fields_to_check.items():
        old_value = old_data.get(field_name, None)
        new_value = getattr(instance, field_name, None)

        # Ensure numeric values are compared correctly
        if field_name == "years_of_study":
            old_value = int(old_value) if old_value is not None else None
            new_value = int(new_value) if new_value is not None else None
        if field_name == "gpa":
            old_value = round(float(old_value), 2) if old_value is not None else None
            new_value = round(float(new_value), 2) if new_value is not None else None

        if safe_compare(old_value, new_value):
            changes.append(f"{field_label} -> {new_value}")

    # Send notification only if there are actual changes
    if changes:
        message = "Your profile has been updated. Changes: " + ", ".join(changes)
        Notification.objects.create(user=instance, message=message)

@receiver(post_save, sender=Feedback)
def send_feedback_notification(sender, instance, created, **kwargs):
    """
    Sends a notification when a new feedback is created.
    """
    if created:
        # Create a notification for the receiver
        Notification.objects.create(
            user=instance.receiver,
            message=f"You have received new feedback titled '{instance.title}' "
                    f"in the category '{instance.get_category_display()}' from {instance.sender.username}."
        )

@receiver(post_save, sender=Chat)
def send_chat_notification(sender, instance, created, **kwargs):
    """
    Sends a notification to the recipient when a new chat message is sent.
    """
    if created:
        # Ensure the recipient is not the sender
        if instance.sender != instance.recipient:
            Notification.objects.create(
                user=instance.recipient,
                message=f"You have a new message from {instance.sender.username}.",
                read=False
            )

@receiver(post_save, sender=AidProgram)
def notify_on_funding_proposal_submission(sender, instance, created, **kwargs):
    """
    Sends notifications when a funder submits a funding proposal.
    Also logs the submission in the system logs.
    """
    if created:
        # Notify admins about the new funding proposal
        admins = User.objects.filter(is_staff=True)
        for admin in admins:
            Notification.objects.create(
                user=admin,
                message=f"A new funding proposal has been submitted by {instance.proposed_by.username}: {instance.name}."
            )
        
        # Notify the funder that their proposal has been submitted
        Notification.objects.create(
            user=instance.proposed_by,
            message=f"Your funding proposal '{instance.name}' has been submitted for review."
        )
        
        # Log the submission in the system logs
        SystemLog.objects.create(
            action_type='funding_proposal_submission',
            description=f"Funding proposal '{instance.name}' submitted by {instance.proposed_by.username}.",
            user=instance.proposed_by
        )

@receiver(pre_save, sender=AidProgram)
def capture_old_aid_program_values(sender, instance, **kwargs):
    """
    Captures old field values before saving an AidProgram instance.
    """
    if instance.pk:  # Only capture if instance exists
        try:
            old_instance = AidProgram.objects.get(pk=instance.pk)
            old_values[instance.pk] = {
                "name": old_instance.name,
                "status": old_instance.status,
                "approval_status": old_instance.approval_status,
            }
        except AidProgram.DoesNotExist:
            pass  # If instance doesn't exist yet, do nothing

@receiver(post_save, sender=AidProgram)
def notify_on_funding_proposal_status_change(sender, instance, **kwargs):
    """
    Sends notifications when the status of a funding proposal changes.
    Also logs the status change in the system logs.
    """
    if instance.pk not in old_values:
        return  # Skip notifications for new proposals
    old_data = old_values.pop(instance.pk, {})  # Retrieve old values and remove from storage

    # Check if approval_status has changed
    old_approval_status = old_data.get("approval_status", None)
    new_approval_status = instance.approval_status
    if old_approval_status != new_approval_status:
        # Notify the funder about the status change
        Notification.objects.create(
            user=instance.proposed_by,
            message=f"The status of your funding proposal '{instance.name}' has been updated to {instance.get_approval_status_display()}."
        )
        
        # Log the status change in the system logs
        SystemLog.objects.create(
            action_type='funding_proposal_status_change',
            description=f"Funding proposal '{instance.name}' status changed from {old_approval_status} to {new_approval_status}.",
            user=instance.proposed_by
        )

### Notifications and Logs for ApplicationStatus (Student Applications)
@receiver(post_save, sender=ApplicationStatus)
def notify_on_application_submission(sender, instance, created, **kwargs):
    """
    Sends notifications when a student submits an application.
    Also logs the submission in the system logs.
    """
    if created:
        # Notify the aid officer (if assigned)
        if instance.aid_officer:
            Notification.objects.create(
                user=instance.aid_officer,
                message=f"New application received from {instance.student.username} for {instance.aid_program.name}."
            )
        
        # Notify the student that their application has been submitted
        Notification.objects.create(
            user=instance.student,
            message=f"You have successfully applied for {instance.aid_program.name}."
        )
        
        # Log the submission in the system logs
        SystemLog.objects.create(
            action_type='application_submission',
            description=f"New application submitted by {instance.student.username} for {instance.aid_program.name}.",
            user=instance.student
        )

@receiver(pre_save, sender=ApplicationStatus)
def capture_old_application_status_values(sender, instance, **kwargs):
    """
    Captures old field values before saving an ApplicationStatus instance.
    """
    if instance.pk:  # Only capture if instance exists
        try:
            old_instance = ApplicationStatus.objects.get(pk=instance.pk)
            old_values[instance.pk] = {
                "status": old_instance.status,
            }
        except ApplicationStatus.DoesNotExist:
            pass  # If instance doesn't exist yet, do nothing

@receiver(post_save, sender=ApplicationStatus)
def notify_on_application_status_change(sender, instance, **kwargs):
    """
    Sends notifications when the status of an application changes.
    Also logs the status change in the system logs.
    """
    if instance.pk not in old_values:
        return  # Skip notifications for new applications
    old_data = old_values.pop(instance.pk, {})  # Retrieve old values and remove from storage

    # Check if status has changed
    old_status = old_data.get("status", None)
    new_status = instance.status
    if old_status != new_status:
        # Notify the student about the status change
        Notification.objects.create(
            user=instance.student,
            message=f"The status of your application for {instance.aid_program.name} has been updated to {instance.get_status_display()}."
        )
        
        # Log the status change in the system logs
        SystemLog.objects.create(
            action_type='application_status_change',
            description=f"Application status for {instance.student.username} changed from {old_status} to {new_status}.",
            user=instance.student
        )

### System Log ###
@receiver(post_save, sender= Account)
def log_profile_update(sender, instance, created, **kwargs):
     if not created:  # Only log updates, not creations
        SystemLog.objects.create(
            action_type='profile_update',
            description=f"Profile updated for user {instance.username}.",
            user=instance
        )

@receiver(post_save, sender=Feedback)
def log_feedback_submission(sender, instance, created, **kwargs):
    """
    Logs feedback submissions.
    """
    if created:
        SystemLog.objects.create(
            action_type='feedback_submission',
            description=f"Feedback submitted by {instance.sender.username} to {instance.receiver.username}.",
            user=instance.sender
        )

@receiver(post_save, sender=User)
def log_user_registration(sender, instance, created, **kwargs):
    """
    Logs user registrations.
    """
    if created:
        SystemLog.objects.create(
            action_type='user_registration',
            description=f"New user registered: {instance.username}.",
            user=instance
        )

@receiver(post_save, sender=Notification)
def log_notification_sent(sender, instance, created, **kwargs):
    """
    Logs when a notification is sent.
    """
    if created:
        SystemLog.objects.create(
            action_type='notification_sent',
            description=f"Notification sent to user {instance.user.username}: {instance.message}",
            user=instance.user
        )

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Logs when a user successfully logs in.
    """
    ip_address = request.META.get('REMOTE_ADDR', 'Unknown IP')
    SystemLog.objects.create(
        action_type='user_login',
        description=f"User {user.username} logged in from IP {ip_address}.",
        user=user
    )

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    """
    Logs when a user fails to log in.
    """
    ip_address = request.META.get('REMOTE_ADDR', 'Unknown IP') if request else 'Unknown IP'
    username = credentials.get('username', 'Unknown User')
    SystemLog.objects.create(
        action_type='other',
        description=f"Failed login attempt for user {username} from IP {ip_address}",
        user=None  # No user associated with failed login
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """
    Logs when a user successfully logs out.
    """
    SystemLog.objects.create(
        action_type='user_login',
        description=f"User {user.username} logged out.",
        user=user
    )

@receiver(post_save, sender=Chat)
def log_chat_message(sender, instance, created, **kwargs):
    """
    Logs chat messages when they are created or updated.
    """
    if created:
        # Log when a new chat message is created
        SystemLog.objects.create(
            action_type='chat_message',
            description=f"New chat message sent by {instance.sender.username} to {instance.recipient.username}: {instance.message[:50]}...",
            user=instance.sender  # Associate the log with the sender
        )
    else:
        # Log when an existing chat message is updated
        SystemLog.objects.create(
            action_type='chat_message',
            description=f"Chat message updated by {instance.sender.username} to {instance.recipient.username}: {instance.message[:50]}...",
            user=instance.sender  # Associate the log with the sender
        )

@receiver(pre_delete, sender=User)
def log_account_deletion(sender, instance, **kwargs):
    # Log the account deletion in the system logs
    SystemLog.objects.create(
        action_type='profile_deletion',
        description=f"User '{instance.username}' has been deleted.",
        user=instance
    )