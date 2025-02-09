from django.conf import settings
from django.db import models
from django.utils.timezone import now

class AidProgram(models.Model):
    """Model representing an aid program (scholarships, grants, loans, etc.)."""
    
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLOSE', 'Closed'),
    ]
    
    LOCALITY_CHOICES = [
        ('LOCAL', 'Local'),
        ('INTERNATIONAL', 'International'),
    ]
    
    LEVEL_CHOICES = [
        ('UNDERGRADUATE', 'Undergraduate'),
        ('POSTGRADUATE', 'Postgraduate'),
    ]
    
    name = models.CharField(max_length=255)  # Aid program name
    owner = models.CharField(max_length=255)  # Managing entity (e.g., government, private company)
    aid_type = models.CharField(max_length=100)  # Type (scholarship, grant, loan)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)  # Education level
    locality = models.CharField(max_length=20, choices=LOCALITY_CHOICES)  # Local/International
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OPEN')  # Open/Closed
    eligibility = models.TextField(blank=True, null=True)  # Eligibility criteria
    closing_date = models.DateField()  # Application deadline
    required_documents = models.TextField(blank=True, null=True)  # List of required docs (comma-separated)
    max_applicants = models.IntegerField(null=True, blank=True)  # Optional limit on applications
    total_funds = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # Total available funds

    def __str__(self):
        return self.name


class ApplicationStatus(models.Model):
    """Tracks student applications for aid programs."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('additional_info', 'Additional Info Required'),
        ('submitted_to_funder', 'Submitted to Funder'),
    ]

    aid_program = models.ForeignKey(AidProgram, on_delete=models.CASCADE)  # Link to aid program
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications")  # Student applicant
    aid_officer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviews")  # Reviewing officer
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')  # Application status
    last_update = models.DateField(default=now)  # Last update timestamp
    supporting_documents = models.FileField(upload_to="documents/", null=True, blank=True)  # Uploaded docs
    officer_comment = models.TextField(blank=True, null=True)  # Comments from officers
    allocated_funds = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Approved fund amount

    def __str__(self):
        return f"{self.aid_program.name} - {self.student.username} - {self.status}"


class AppealStatus(models.Model):
    """Handles appeals for rejected applications."""

    application = models.ForeignKey(ApplicationStatus, on_delete=models.CASCADE)  # Link to application
    appeal_reason = models.TextField()  # Reason for appeal
    appeal_date = models.DateField(default=now)  # Date appeal was submitted
    appeal_status = models.CharField(
        max_length=10,
        choices=[
            ('PENDING', 'Pending'),
            ('APPROVED', 'Approved'),
            ('REJECTED', 'Rejected'),
        ],
        default='PENDING'
    )

    def __str__(self):
        return f"Appeal for {self.application.aid_program.name} - {self.appeal_status}"
