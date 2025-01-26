from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import GeneralInfo, StudentSignUp, FunderSignUp
from .models import Account

# Sign up step 1
def signup_step1(request):
    if request.method == 'POST':
        form = GeneralInfo(request.POST)
        if form.is_valid():
            # Save the form data to the session
            request.session['signup_data'] = {
                'username': form.cleaned_data['username'],
                'email': form.cleaned_data['email'],
                'password': form.cleaned_data['password'],
                'phone_number': form.cleaned_data['phone_number'],
                'role': form.cleaned_data['role'],
            }
            return redirect('signup_step2')
    else:
        # Repopulate the form with session data if available
        signup_data = request.session.get('signup_data', {})
        form = GeneralInfo(initial=signup_data)

    return render(request, 'users/signup_step1.html', {'form': form})

def signup_step2(request):
    signup_data = request.session.get('signup_data', {})
    role = signup_data.get('role')

    if role == 'student':
        form_class = StudentSignUp
    elif role == 'funder':
        form_class = FunderSignUp
    else:
        # No additional form needed for 'officer'
        form_class = None

    if request.method == 'POST':
        if form_class is not None:
            # Handle forms for student and funder
            form = form_class(request.POST)
            if form.is_valid():
                # Save additional form data to the session
                if role == 'student':
                    signup_data.update({
                        'study_program': form.cleaned_data['study_program'],
                        'years_of_study': form.cleaned_data['years_of_study'],
                        'gpa': form.cleaned_data['gpa'],
                    })
                elif role == 'funder':
                    signup_data.update({
                        'organization_name': form.cleaned_data['organization_name'],
                    })

                request.session['signup_data'] = signup_data
        else:
            # No form to process for officer
            pass

        # Create user and handle approval for officer and funder
        is_approved = role not in ['officer', 'funder']

        user = Account.objects.create_user(
            username=signup_data['username'],
            email=signup_data['email'],
            password=signup_data['password'],
            phone_number=signup_data['phone_number'],
            role=signup_data['role'],
            study_program=signup_data.get('study_program'),
            years_of_study=signup_data.get('years_of_study'),
            gpa=signup_data.get('gpa'),
            organization_name=signup_data.get('organization_name'),
            is_approved=is_approved,
        )

        if role in ['officer', 'funder']:
            return redirect('approval_pending')
        else:
            return redirect('login')
    else:
        # Repopulate the form with session data if available
        if form_class is not None:
            form = form_class(initial=signup_data)
        else:
            form = None

    return render(request, 'users/signup_step2.html', {'form': form, 'role': role})

def approval_pending(request):
    return render(request, 'users/approval_pending.html')

def login(request):
    return render(request, 'users/login.html')