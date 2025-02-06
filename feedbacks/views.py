# feedbacks/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import Feedback
from .forms import FeedbackForm
from users.models import Account

@login_required
def feedback_view(request):
    tab = request.GET.get('tab', 'received')
    feedback_id = request.GET.get('id')

    # Get all feedback (both sent and received by the logged-in user)
    all_feedbacks = Feedback.objects.filter(
        models.Q(sender=request.user) | models.Q(receiver=request.user)
    ).order_by('-created_at')

    # Add a computed field for feedback type ('Sent' or 'Received')
    feedback_list = []
    for feedback in all_feedbacks:
        feedback_data = {
            'feedback': feedback,
            'type': 'Sent' if feedback.sender == request.user else 'Received',
        }
        feedback_list.append(feedback_data)

    # Handle viewing a specific feedback
    if tab == 'view' and feedback_id:
        feedback = get_object_or_404(Feedback, id=feedback_id)
        if feedback.receiver == request.user and not feedback.is_read:
            feedback.is_read = True
            feedback.save()
        return render(request, 'feedbacks/feedback.html', {
            'tab': tab,
            'feedback': feedback,
            'feedback_list': feedback_list,
        })

    # Handle replying to feedback
    if tab == 'reply' and feedback_id:
        feedback = get_object_or_404(Feedback, id=feedback_id, receiver=request.user)
        return render(request, 'feedbacks/feedback.html', {
            'tab': tab,
            'feedback': feedback,
            'feedback_list': feedback_list,
        })

    # Default view: Show the combined feedback table
    return render(request, 'feedbacks/feedback.html', {
        'tab': tab,
        'feedback_list': feedback_list,
    })

@login_required
def send_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.sender = request.user

            # Determine the receiver based on the category
            category = form.cleaned_data['category']
            if category == 'system/application':
                feedback.receiver = Account.objects.filter(role='administrator').first()
            elif category == 'aid_programs':
                feedback.receiver = Account.objects.filter(role='officer').first() or Account.objects.filter(role='funder').first()

            feedback.save()
            return redirect('feedback_view')  # Redirect back to the feedback view
    return redirect('feedback_view')

@login_required
def reply_feedback(request, feedback_id):
    if request.method == 'POST':
        feedback = get_object_or_404(Feedback, id=feedback_id, receiver=request.user)
        message = request.POST.get('message')

        # Create a new feedback as a reply
        Feedback.objects.create(
            sender=request.user,
            receiver=feedback.sender,  # Reply goes back to the original sender
            title=f"Re: {feedback.title}",
            message=message,
            category=feedback.category,
        )
        return redirect('feedback_view')
    return redirect('feedback_view')