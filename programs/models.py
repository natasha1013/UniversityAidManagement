from django.conf import settings
from django.db import models
from django.utils.timezone import now

# The AidProgram model stores details about different aid programs available for students.
from django.conf import settings
from django.db import models
from django.utils.timezone import now

class AidProgram(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLOSE', 'Close'),
    ]
    
    LOCALITY_CHOICES = [
        ('LOCAL', 'Local'),
        ('INTERNATIONAL', 'International'),
    ]
    
    LEVEL_CHOICES = [
        ('UNDERGRADUATE', 'Undergraduate'),
        ('POSTGRADUATE', 'Postgraduate'),
    ]

    APPROVAL_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    name = models.CharField(max_length=255)
    owner = models.CharField(max_length=255)
    aid_type = models.CharField(max_length=100)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    locality = models.CharField(max_length=20, choices=LOCALITY_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OPEN')
    eligibility = models.TextField(blank=True, null=True)
    closing_date = models.DateField()
    required_documents = models.TextField(blank=True, null=True)
    total_funds = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    proposed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    approval_status = models.CharField(max_length=10, choices=APPROVAL_CHOICES, default='PENDING')

    def __str__(self):
        return self.name

# The ApplicationStatus model keeps track of students' applications for aid programs.
class ApplicationStatus(models.Model):
    # Different statuses an application can have.
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('additional_info', 'Additional Info Required'),
        ('submitted_to_funder', 'Submitted to Funder'),
    ]

    aid_program = models.ForeignKey(AidProgram, on_delete=models.CASCADE)  
    # Links each application to a specific aid program.
    
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)    # Links the application to a student (user model).
    # If the student is deleted, the application is also deleted.

    aid_officer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviews")  
    # Links the application to an aid officer who reviews it.
    # If the officer is deleted, their record is set to NULL instead of deleting the application.

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')  
    # Tracks the current status of the application.
    
    last_update = models.DateField(default=now)  
    # Stores the last updated date of the application (defaults to the current date).

    supporting_document = models.FileField(upload_to="documents/", null=True, blank=True)  
    # Optional field for students to upload supporting documents.

    officer_comment = models.TextField(blank=True, null=True)  
    # Field for the reviewing officer to leave comments on the application.

    allocated_funds = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  
    # Optional field to store the amount of funds allocated to the applicant.
    


    def __str__(self):
        return f"{self.student.username} - {self.aid_program.name} - {self.status}"  
    # Returns the aid program name and current status when printed.

# The AppealStatus model tracks appeals submitted by students if their application was rejected.
class AppealStatus(models.Model):
    application = models.ForeignKey(ApplicationStatus, on_delete=models.CASCADE)  
    # Links each appeal to a specific application.

    appeal_reason = models.TextField()  
    # Stores the reason why the student is appealing.

    appeal_date = models.DateField(default=now)  
    # Records the date when the appeal was submitted (defaults to the current date).

    appeal_status = models.CharField(
        max_length=10,
        choices=[
            ('PENDING', 'Pending'),
            ('APPROVED', 'Approved'),
            ('REJECTED', 'Rejected'),
        ],
        default='PENDING'
    )  
    # Tracks the status of the appeal (default is Pending).

    def __str__(self):
        return f"Appeal for {self.application.aid_program.name} - {self.appeal_status}"  
    # Returns a string indicating the aid program and appeal status when printed.
