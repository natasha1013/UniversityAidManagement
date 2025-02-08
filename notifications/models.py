from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"

    class Meta:
        db_table = 'notifications_table'  # Custom table name

class SystemLog(models.Model):
    ACTION_TYPES = [
        ('profile_update', 'Profile Update'),
        ('feedback_submission', 'Feedback Submission'),
        ('notification_sent', 'Notification Sent'),
        ('user_registration', 'User Registration'),
        ('user_login', 'User Login'), 
        ('other', 'Other'),
    ]

    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_logs')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_action_type_display()} - {self.timestamp}"

    class Meta:
        db_table = 'systemlog_table'
        ordering = ['-timestamp']  # Order logs by most recent first