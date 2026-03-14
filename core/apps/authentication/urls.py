from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from . import views

urlpatterns = [
    path("login/", views.CustomAuthToken.as_view()),
    path("sginup/", views.ReigsterView.as_view()),
    path("logout/", views.LogoutView.as_view()),
    path(
        "verify-email/", views.verify_email, name="verify_email"
    ),  # Fixed: was check_email_velidate
    path("send-verify-email/", views.send_verify_email, name="send_verify_email"),
    # New secure password reset endpoints
    path(
        "password-reset-request/",
        views.PasswordResetRequestView.as_view(),
        name="password-reset-request",
    ),
    path(
        "password-reset-confirm/",
        views.PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    # Legacy endpoint (deprecated - use the new ones above)
    path("reset-password/", views.PasswordResetView.as_view(), name="reset-password"),
]
