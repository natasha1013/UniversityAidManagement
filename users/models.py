# any changes, make sure to 'python manage.py makemigrations' and 'python manage.py migrate'

from django.db import models
from django.contrib.auth.models import AbstractUser #Extension of AbstractUser
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

    # username            = models.CharField(max_length=150, unique=True)
    role                = models.CharField(max_length=13, choices=ROLE_LIST)
    study_program       = models.CharField(max_length=100, blank=True, null=True) # only for Students
    years_of_study      = models.IntegerField(blank=True, null=True)
    gpa                 = models.FloatField(blank=True, null=True)
    organization_name   = models.CharField(max_length=255, blank=True, null=True)
    is_approved         = models.BooleanField(default=False)
    phone_number        = models.CharField(max_length=15, blank=True, null=True)
    created_at          = models.DateTimeField(default=now)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users_masterlist'

    def __str__(self):
        return self.username