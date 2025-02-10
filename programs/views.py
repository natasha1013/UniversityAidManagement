from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import AidProgram, ApplicationStatus, AppealStatus
from .forms import AidProgramForm
from django.http import HttpResponseRedirect
from django.urls import reverse

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

# Aid Officer
def all_aid_list(request):
    aids = AidProgram.objects.all()
    return render(request, 'all_aids.html', {'all_aids': aids})

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

#admin
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