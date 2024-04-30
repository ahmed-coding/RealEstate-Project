from django.shortcuts import render
import json

# Create your views here.

from rest_framework import viewsets
from rest_framework import status
from rest_framework import filters
from . import serializers
from ..models import FriendList, User
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from ..models import FriendList, PrivateChatRoom, User
from django.db.models import Q


class FriendView(viewsets.ModelViewSet):
    serializer_class = serializers.FrindListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user or None
        # return FriendList.objects.filter(
        #     Q(user1=user) | Q(user2=user)
        # )
        return FriendList.objects.filter(user=user).order_by('-id')

    def get_serializer_context(self):
        return {'user': self.request.user}
