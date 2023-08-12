from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_str, force_bytes
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.conf import settings
from django.core.mail import send_mail
import uuid
from typing import Protocol
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, Http404
from django.views.generic import RedirectView
from django.views.generic import UpdateView, ListView
from django.utils.decorators import method_decorator


from .forms import SignUpForm, PatientProfileEdit
from .models import PatientProfile, User, CustomUser
from .decorators import role_required

User = get_user_model()


@role_required(allowed_role="PATIENT")
def verify(request, auth_token):
    uid = uuid.UUID(auth_token)
    try:
        profile_obj = get_user_model().objects.get(auth_token=auth_token)
        if profile_obj:
            if profile_obj.is_active:
                messages.success(request, 'Your account is already verified.')
                return redirect('already_verified')
            profile_obj.is_active = True
            try:
                profile_obj.save()
            except Exception as e:
                message = f'this is an error from verify view first place {e}'
                return redirect('error')
            messages.success(request, 'Your account has been verified.')
            return redirect('login')
        else:
            return redirect('signup')
    except Exception as e:
        message = f'this is an error from verify view second place{e}'
        return redirect('error')


def sign_up(request):
    form = SignUpForm()  # Use UserCreationForm instead of SignUpForm
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            # user = form.save(commit=False)
            # auth_token = str(uuid.uuid4())
            # user.auth_token = auth_token
            # user.is_active = False
            # send_mail_after_registration(user.email, auth_token)
            # activate_email(request, user, form.cleaned_data.get('email'))
            user = form.save(request)
            auth_login(request, user)
            return redirect('email_sent')

        else:
            for e in list(form.errors.values()):
                message = f'this is an error from sign up view {e}'
                return redirect('error')
    return render(request, 'signup.html', {'form': form})


@login_required
def patient_profile(request, user_id):
    # user = get_user_model().objects.get(pk=id)
    try:
        user = get_user_model().objects.get(pk=user_id)
    except get_user_model().DoesNotExist:
        raise Http404
    return render(request, 'patient_profile.html', {'user': user})


@login_required
@role_required("PATIENT")
def patient_edit_profile(request, user_id):
    form = PatientProfileEdit(instance=request.user)
    if request.method == 'POST':
        form = PatientProfileEdit(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(request, user_id)
            auth_login(request, user)
            return redirect('patient_profile', user_id=user.id)

        else:
            for e in list(form.errors.values()):
                message = f'this is an error from patient_edit_profile view {e}'
                return redirect('error')
    return render(request, 'edit_patient_profile.html', {'form': form})


@login_required
def appointment(request):
    if request.method == 'POST':
        subject = request.POST['subject']
        patient_email = request.POST['patient_email']
        message = request.POST['message']
        recipient_list = ['osoundous917@gmail.com']
        send_mail(subject, message, patient_email, recipient_list)
        return redirect('success')

    return render(request, 'appointment.html')


@login_required
@role_required("DOCTOR")
def patients(request):
    users = get_user_model().objects.all().order_by('-date_joined')
    return render(request, 'patients.html', {'users': users})


@method_decorator(login_required, 'dispatch')
@role_required("DOCTOR")
class PatientsList(ListView):
    model = CustomUser
    context_object_name = 'users'
    template_name = 'patients.html'


def doctor_profile(request):
    return render(request, 'doctor_profile.html')

