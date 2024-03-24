from django.shortcuts import render
import json

# Create your views here.

from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import filters
from . import serializers
from ..models import FriendList, User

class FriendView(viewsets.ModelViewSet):

    queryset = FriendList.objects.all()
    print()
    serializer_class = serializers.FrindListSerializer
    print()

    def perform_create(self, serializer):
        # Set the user for the newly created FriendList instance
        serializer.save(user=self.request.user)


