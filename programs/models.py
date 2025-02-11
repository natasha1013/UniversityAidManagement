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
        ('SUBMIT TO FUNDERS', 'Submit to Funders'),
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
    approval_status = models.CharField(max_length=20, choices=APPROVAL_CHOICES, default='PENDING')

    def __str__(self):
        return self.name

class ApplicationStatus(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('additional_info', 'Additional Info Required'),
        ('submitted_to_funder', 'Submitted to Funder'),
    ]

    aid_program = models.ForeignKey(AidProgram, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    aid_officer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviews")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    last_update = models.DateField(default=now)
    supporting_document = models.FileField(upload_to="documents/", null=True, blank=True)
    officer_comment = models.TextField(blank=True, null=True)
    allocated_funds = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def can_track_fund_utilization(self):
        return self.status == "approved"

class AppealStatus(models.Model):
    application = models.ForeignKey(ApplicationStatus, on_delete=models.CASCADE)  
    appeal_reason = models.TextField()
    appeal_date = models.DateField(default=now)  
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

class FundUtilization(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    aid_program = models.ForeignKey(AidProgram, on_delete=models.CASCADE)
    category = models.CharField(
        max_length=50, 
        choices=[
            ('TUITION', 'Tuition'),
            ('LIVING', 'Living Expenses'),
            ('BOOKS', 'Books'),
            ('RESEARCH', 'Research'),
            ('OTHER', 'Other')
        ]
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    transaction_date = models.DateField(default=now)
    flagged = models.BooleanField(default=False)
    acknowledged_by_funder = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.username} - {self.aid_program.name} - {self.category} - {self.amount}"



