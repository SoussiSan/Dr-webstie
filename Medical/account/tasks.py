from celery import shared_task
from .models import CustomUser
from django.contrib.auth import get_user_model


@shared_task
def delete_unconfirmed_user(user_id):
    user = get_user_model().objects.get(pk=user_id)
    if user.is_active == False:
        user.delete()
