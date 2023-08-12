import datetime
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, AbstractUser, User
# from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        DOCTOR = "DOCTOR", "Doctor"
        PATIENT = "PATIENT", "Patient"
    base_role = Role.PATIENT

    role = models.CharField(max_length=50, choices=Role.choices)
    email = models.EmailField(unique=True)
    date_birth = models.DateField(default=datetime.date(1990, 1, 7))
    phone = models.CharField(max_length=12, null=True)
    picture = models.ImageField(upload_to='static/img/', null=True)
    address = models.CharField(null=True, max_length=250)
    auth_token = models.CharField(max_length=100, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
            return super().save(*args, **kwargs)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class DoctorManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.DOCTOR)


class Doctor(CustomUser):
    base_role = CustomUser.Role.DOCTOR
    doctor = DoctorManager()

    class Meta:
        proxy = True


class DoctorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="doctor")
    specialities = models.CharField(default='generalist', max_length=200)


@receiver(post_save, sender=Doctor)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == "DOCTOR":
        DoctorProfile.objects.create(user=instance)


class PatientManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=CustomUser.Role.PATIENT)


class Patient(CustomUser):
    base_role = CustomUser.Role.PATIENT
    patient = PatientManager()

    class Meta:
        proxy = True

    @property
    def ShwoPatientProfile(self):
        return self.Patientprofile


@receiver(post_save, sender=Patient)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == "PATIENT":
        PatientProfile.objects.create(user=instance)


class PatientProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="patient")
    blood_group = models.CharField(default='o+', max_length=6)
    allergic_to = models.CharField(max_length=200, null=True)
    gender = models.CharField(max_length=10)

    def age(self):
        current_date = datetime.date.today()
        p_age = current_date.year - self.user.date_birth.year
        return p_age

    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def __str__(self):
        return self.user.email




