from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_or_return_private_chat, name='create-chat'),
    path('rooms/', views.list_chat_rooms, name='list-chat-rooms'),
]
