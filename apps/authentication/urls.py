from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from . import views
urlpatterns = [
    path('login/', views.CustomAuthToken.as_view()),
    path('sginup/', views.ReigsterView.as_view()),
    # path('logout/',)
]
