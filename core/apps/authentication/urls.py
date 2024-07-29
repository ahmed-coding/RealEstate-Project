from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from . import views
urlpatterns = [
    path('login/', views.CustomAuthToken.as_view()),
    path('sginup/', views.ReigsterView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('verify-email/', views.check_email_velidate, name='verify_email'),
    path('send-verify-email/', views. send_verify_email, name='send_verify_email'),
    path('reset-password/', views.PasswordResetView.as_view(),
         name='reset-password /'),


]
