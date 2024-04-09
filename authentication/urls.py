from django.contrib import admin
from django.urls import path, include
from . import views
from .views import signupView, LoginView, UsernameValidationView, EmailValidationView, LogoutView, EditProfileView
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('signup/', signupView.as_view(), name="signup"),
    path('validate-username', csrf_exempt(UsernameValidationView.as_view()), name="validate-username"),
    path('validate-email', csrf_exempt(EmailValidationView.as_view()), name="validate-email"),
    path('login/', csrf_exempt(LoginView.as_view()), name="login"),
    path('edit-profile/', EditProfileView.as_view(), name="edit_profile"),
    path('logout/', LogoutView.as_view(), name='logout'),  # Add this line for the logout view
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

