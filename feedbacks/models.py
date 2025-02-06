# feedbacks/models.py
from django.conf import settings  # Import settings instead of directly importing Account
from django.db import models

class Feedback(models.Model):
    # Define the category choices
    CATEGORY_CHOICES = [
        ('system/application', 'System/Application'),
        ('aid_programs', 'Aid Programs'),
    ]

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_feedbacks', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_feedbacks', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    attachment = models.FileField(upload_to='feedback_attachments/', blank=True, null=True)
    is_read = models.BooleanField(default=False)  # Track if the feedback is read
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - from {self.sender.username} to {self.receiver.username}"

    class Meta:
        db_table = 'feedback'