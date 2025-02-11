from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import AidProgram, ApplicationStatus, AppealStatus, FundUtilization
from .forms import AidProgramForm, FundUtilizationForm
from django.http import HttpResponseRedirect
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.timezone import now



# 🚀 **Automatically create FundUtilization when Aid is Approved**
@receiver(post_save, sender=ApplicationStatus)
def create_fund_utilization(sender, instance, created, **kwargs):
    """
    Automatically creates an initial fund utilization record when an application is approved.
    """
    if instance.status == "approved":
        # Check if a fund utilization record already exists
        existing_records = FundUtilization.objects.filter(student=instance.student, aid_program=instance.aid_program).exists()
        if not existing_records:
            FundUtilization.objects.create(
                student=instance.student,
                aid_program=instance.aid_program,
                category="OTHER",
                amount=0.00,  # Start with 0, students can update later
                description="Initial record created upon approval.",
                transaction_date=now()
            )


# Student

def aid_list(request):
    aids = AidProgram.objects.filter(approval_status="APPROVED", status="OPEN")
    return render(request, 'aid_list.html', {'aids': aids})


def aid_details(request, aid_id):
    """Show details of a specific aid program."""
    aid_program = get_object_or_404(AidProgram, id=aid_id)
    return render(request, 'aid_details.html', {'aid_program': aid_program})


@login_required
def apply_for_aid(request, aid_id):
    """Allow students to apply for an aid program."""
    aid_program = get_object_or_404(AidProgram, id=aid_id)
    
    # Check if the aid program is closed
    if aid_program.status.lower() == "closed":
        messages.error(request, "This scholarship is closed.")
        return redirect('aid_details', aid_id=aid_id)

    application, created = ApplicationStatus.objects.get_or_create(
        aid_program=aid_program,
        student=request.user,
        defaults={'status': 'pending'}
    )

    if created:
        messages.success(request, "You have successfully applied for this aid program!")
    else:
        messages.warning(request, "You have already applied for this aid program.")

    return redirect('aid_details', aid_id=aid_id)


@login_required
def application_status_view(request):
    """Allow students to view the status of their applications."""
    applications = ApplicationStatus.objects.filter(student=request.user)
    return render(request, 'application_status.html', {'applications': applications})

@login_required
def student_fund_utilization(request):
    student = request.user

    # Get the student's approved applications
    approved_apps = ApplicationStatus.objects.filter(student=student, status="approved")

    # Get existing fund utilization records
    fund_utilizations = FundUtilization.objects.filter(student=student)

    if request.method == "POST":
        form = FundUtilizationForm(request.POST)
        if form.is_valid():
            
            fund_utilization = form.save(commit=False)
            fund_utilization.student = student
            fund_utilization.aid_program_id = request.POST.get("aid_program")  # Set manually

            # Ensure they are updating an approved aid program
            if not ApplicationStatus.objects.filter(student=student, aid_program=fund_utilization.aid_program, status="approved").exists():
                return redirect("student_fund_utilization")  # Prevent unauthorized entries
            
            fund_utilization.save()
            return redirect("student_fund_utilization")
    else:
        form = FundUtilizationForm()

    return render(request, "student_fund_utilization.html", {
        "form": form,
        "fund_utilizations": fund_utilizations,
        "approved_apps": approved_apps,
    })


# Aid Officer

def manage_aid_applications(request):

    applications = ApplicationStatus.objects.filter(status="pending")
    return render(request, "manage_aid_applications.html", {"applications": applications})


@login_required
def review_application(request, application_id):
    """Aid officers can review applications and update statuses."""
    application = get_object_or_404(ApplicationStatus, id=application_id)


    if request.method == "POST":
        application.status = request.POST.get("status")
        application.officer_comment = request.POST.get("officer_comment", "")
        application.aid_officer = request.user
        application.save()
        messages.success(request, "Application status updated successfully.")

        return redirect(f'/profile/?tab=aid_application')\
            
    return render(request, "review_application.html", {"application": application})

def aid_officer_monitor_utilization(request):
    """ Aid officers can monitor and flag suspicious transactions """
    utilizations = FundUtilization.objects.all()
    return render(request, 'aid_officer_utilization.html', {'utilizations': utilizations})

def flag_fund_utilization(request, utilization_id):
    """ Aid officers can flag transactions for review """
    utilization = get_object_or_404(FundUtilization, id=utilization_id)
    utilization.flagged = True
    utilization.save()
    messages.warning(request, "Fund utilization has been flagged for review.")
    return redirect('aid_officer_utilization')




#Funders

def propose_aid_program(request):
    """Allow funders to propose a new aid program."""
    if request.method == "POST":
        form = AidProgramForm(request.POST)
        if form.is_valid():
            aid_program = form.save(commit=False)
            aid_program.proposed_by = request.user
            aid_program.approval_status = "PENDING"
            aid_program.save()
            messages.success(request, "Aid program proposal submitted successfully! Waiting for admin approval.")
            return redirect(f'/profile/?tab=status')

    else:
        form = AidProgramForm()
    
    return render(request, "propose_aid_program.html", {"form": form})

def my_proposals(request):
    """Funders can view the status of their submitted aid proposals."""
    my_aids = AidProgram.objects.filter(proposed_by=request.user)
    return render(request, "my_proposals.html", {"my_aids": my_aids})


def funder_review_applications(request):
    """List all applications that need funder approval."""
    applications = ApplicationStatus.objects.filter(status="submitted_to_funder")

    return render(request, "funder_review_applications.html", {"applications": applications})


def funder_approve_application(request, application_id):
    """Funders approve an application."""
    application = get_object_or_404(ApplicationStatus, id=application_id)
    application.status = "approved"
    application.save()
    messages.success(request, "Application approved successfully.")
    return redirect("/profile/?tab=aid_application")

def funder_reject_application(request, application_id):
    """Funders reject an application."""
    application = get_object_or_404(ApplicationStatus, id=application_id)
    application.status = "rejected"
    application.save()
    messages.error(request, "Application rejected.")
    return redirect("/profile/?tab=aid_application")


def funder_view_utilization(request):
    """ Funders can view fund utilization """
    utilizations = FundUtilization.objects.all()
    return render(request, 'funder_utilization.html', {'utilizations': utilizations})

def acknowledge_fund_utilization(request, utilization_id):
    """ Updates the acknowledgment status of a fund utilization record """
    utilization = get_object_or_404(FundUtilization, id=utilization_id)
    
    if not utilization.acknowledged_by_funder:  # Only update if not already acknowledged
        utilization.acknowledged_by_funder = True
        utilization.save()
        messages.success(request, "Fund utilization has been acknowledged.")
    
    return redirect('funder_utilization')  # Redirect back to the list

#admin

def all_aid_list(request):
    aids = AidProgram.objects.all()
    return render(request, 'all_aids.html', {'all_aids': aids})

def edit_aid(request, aid_id):
    aid = get_object_or_404(AidProgram, id=aid_id)
    if request.method == "POST":
        form = AidProgramForm(request.POST, instance=aid)
        if form.is_valid():
            form.save()
            return redirect('all_aids')  # Redirect back to the list
    else:
        form = AidProgramForm(instance=aid)
    return render(request, 'edit_aid.html', {'form': form})

def review_aid_program(request):
    """Admin can review and approve/reject proposed aid programs."""
    pending_aids = AidProgram.objects.filter(approval_status="PENDING")
    
    return render(request, "review_aid_program.html", {"pending_aids": pending_aids})

def approve_aid(request, aid_id):
    """Admin approves an aid program."""
    aid_program = get_object_or_404(AidProgram, id=aid_id)
    aid_program.approval_status = "APPROVED"
    aid_program.save()
    messages.success(request, "Aid program approved successfully.")
    return redirect("review_aid_program")

def reject_aid(request, aid_id):
    """Admin rejects an aid program."""
    aid_program = get_object_or_404(AidProgram, id=aid_id)
    aid_program.approval_status = "REJECTED"
    aid_program.save()
    messages.error(request, "Aid program rejected.")
    return redirect("review_aid_program")