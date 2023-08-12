from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from .models import Doctor, Patient, CustomUser, PatientProfile
from django.db import transaction
from django.conf import settings
from django.core.mail import send_mail
import uuid
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_str, force_bytes
from django.template.loader import render_to_string
from django.contrib import messages
from .tokens import account_activation_token
from .tasks import delete_unconfirmed_user
from phonenumber_field.formfields import PhoneNumberField
from django.core.validators import RegexValidator


# reg = r'^0[5-7]\d{8}$'
phone_regex = RegexValidator(r'^0[5-7]\d{8}$', "enter a valid algerian phone number please")
my_validator = RegexValidator(r"A", "Your string should contain letter A in it.")


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=255, required=True)
    first_name = forms.CharField(max_length=200, required=True)
    last_name = forms.CharField(max_length=200, required=True)
    username = forms.CharField(max_length=200, required=True)
    date_birth = forms.DateField(required=True)
    blood_group = forms.ChoiceField(required=True, choices=(('O+', 'O+'), ('A+', 'A+'), ('B+', 'B+'), ('AB+', 'AB+'), ('O-', 'O-'), ('A-', 'A-'), ('B-', 'B-'), ('AB-', 'AB-')))
    phone = forms.CharField(required=True, validators=[phone_regex])
    # phone = PhoneNumberField(required=True)
    picture = forms.ImageField(required=True)
    allergic_to = forms.CharField(required=False)
    address = forms.CharField(max_length=255, required=False)
    gender = forms.ChoiceField(required=True, choices=(('female', 'Female'), ('male', 'male')))

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'date_birth', 'blood_group'
                 , 'phone', 'picture', 'allergic_to', 'address', 'gender']

    @transaction.atomic
    def save(self, request, *args, **kwargs):
        user = super().save(commit=False)
        # user.is_active = True
        # user.first_name = self.cleaned_data.get('first_name')
        # user.last_name = self.cleaned_data.get('last_name')
        auth_token = str(uuid.uuid4())
        user.auth_token = auth_token
        user.is_active = False
        send_mail_after_registration(request, user.email, auth_token)
        user.save()
        # delete_unconfirmed_user(user.id).apply_async(countdown=1 * 60 * 60)
        patient = PatientProfile.objects.create(user=user)
        patient.phone = self.cleaned_data.get('phone')
        patient.allergic_to = self.cleaned_data.get('allergic_to')
        patient.gender = self.cleaned_data.get('gender')
        patient.address = self.cleaned_data.get('address')
        patient.blood_group = self.cleaned_data.get('blood_group')
        patient.save()
        return user


def send_mail_after_registration(request, email, token):
    # url = f'http://{get_current_site()}'
    subject = 'Your accounts need to be verified'
    message = f'Hi paste the link to verify your account {get_current_site(request).domain}/verify/{token}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    # send_mail(subject, message, email_from, recipient_list)
    email = EmailMessage(subject, message, to=[email])
    if email.send():
        return messages.success(request, f'Dear <b>User</b>, please go to you email <b>{email}</b> inbox and click on \
                    received activation link to confirm and complete the registration. <b>Note:</b> Check your spam folder')
    else:
        return messages.error(request, f'Problem sending email to {email}, check if you typed it correctly.')


class PatientProfileEdit(UserChangeForm):
    email = forms.EmailField(max_length=255, required=False)
    phone = forms.CharField(required=False, validators=[phone_regex])
    #phone = PhoneNumberField(required=True)
    picture = forms.ImageField(required=False)
    allergic_to = forms.CharField(required=False)
    address = forms.CharField(max_length=255, required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ['email', 'phone', 'picture', 'allergic_to', 'address']

    @transaction.atomic
    def save(self, request, user_id, *args, **kwargs):
        user = CustomUser.objects.get(pk=user_id)
        old_email = user.email
        # user.super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        user.picture = self.cleaned_data.get('picture')
        user.address = self.cleaned_data.get('address')
        user.phone = self.cleaned_data.get('phone')
        if old_email != user.email:
            auth_token = str(uuid.uuid4())
            user.auth_token = auth_token
            user.is_active = False
            send_mail_after_registration(request, user.email, auth_token)
        user.save()
        patient = PatientProfile.objects.get(user=user)
        patient.allergic_to = self.cleaned_data.get('allergic_to')
        patient.save()
        return user


# dose not used
def activate_email(request, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string("activate_account.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        return messages.success(request, f'Dear <b>{user}</b>, please go to you email <b>{to_email}</b> inbox and click on \
                received activation link to confirm and complete the registration. <b>Note:</b> Check your spam folder')
    else:
        return messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')





