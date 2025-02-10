from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import AidProgram, ApplicationStatus, AppealStatus

def aid_list(request):
    aids = AidProgram.objects.all()
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

    return render(request, "review_application.html", {"application": application})
