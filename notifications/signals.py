from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Notification
from users.models import Account
from feedbacks.models import Feedback

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