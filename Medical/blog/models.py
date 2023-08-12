from django.db import models
from account.models import CustomUser, PatientProfile, DoctorProfile
from django.utils.text import Truncator

# Create your models here.


class Post(models.Model):
    message = models.CharField(max_length=400)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_dt = models.DateTimeField(null=True)
    views = models.PositiveIntegerField(default=0)
    picture = models.ImageField(upload_to='static/img/posts/', null=True)
    title = models.CharField(max_length=50)


    def short_message(self):
        short = Truncator(self.message)
        return short.chars(80)
