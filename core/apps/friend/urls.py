from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.FriendView.as_view({'get': 'list'})),
]