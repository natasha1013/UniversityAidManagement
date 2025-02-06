# any changes, make sure to 'python manage.py makemigrations' and 'python manage.py migrate'
from django.db import models
from django.contrib.auth.models import AbstractUser  # Extension of AbstractUser
from django.utils.timezone import now

# Create your models here.
class Account(AbstractUser):
    # only available roles
    ROLE_LIST = [
        ('student', 'Student'),
        ('officer', 'Aid Officer'),
        ('funder', 'Funder'),
        ('administrator', 'Administrator'),
    ]

    role = models.CharField(max_length=13, choices=ROLE_LIST)
    study_program = models.CharField(max_length=100, blank=True, null=True)  # only for Students
    years_of_study = models.IntegerField(blank=True, null=True)
    gpa = models.FloatField(blank=True, null=True)
    organization_name = models.CharField(max_length=255, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users_masterlist'

    def __str__(self):
        return self.username

    # Feedback-related methods
    def unread_feedback_count(self):
        """
        Returns the number of unread feedback messages for the user.
        """
        return self.received_feedbacks.filter(is_read=False).count()

    def mark_feedback_as_read(self, feedback_id):
        """
        Marks a specific feedback as read by its ID.
        """
        try:
            feedback = self.received_feedbacks.get(id=feedback_id)
            feedback.is_read = True
            feedback.save()
        except models.ObjectDoesNotExist:
            pass  # Handle the case where the feedback doesn't exist

    def mark_all_feedback_as_read(self):
        """
        Marks all feedback as read for the user.
        """
        self.received_feedbacks.filter(is_read=False).update(is_read=True)