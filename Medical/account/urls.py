from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('signup/', views.sign_up, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    # path('activate/<str:uidb64>/<str:token>', views.activate, name='activate'),
    path('verify/<auth_token>', views.verify, name="verify"),
    path('profile/<int:user_id>', views.patient_profile, name='patient_profile'),
    path('profile/<int:user_id>/edit', views.patient_edit_profile, name='edit_patient_profile'),
    path('success/', TemplateView.as_view(template_name='success.html'), name='success'),
    path('error/', TemplateView.as_view(template_name='error.html'), name='error'),
    path('already_verified/', TemplateView.as_view(template_name='already_verified.html'), name='already_verified'),
    path('email_sent/', TemplateView.as_view(template_name='email_sent.html'), name='email_sent'),
    path('appointment', views.appointment, name='appointment'),
    path('doctor_profile/', views.doctor_profile, name='doctor_profile'),

    # path('patients/', views.PatientsList.as_view(), name='patients'),
    path('patients/', views.patients, name='patients')
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
