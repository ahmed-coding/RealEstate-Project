from django.shortcuts import render
from rest_framework import viewsets
from apps.models import Image
from . import serializers
from rest_framework.permissions import IsAuthenticated

# Create your views here.


class ImageViewsets(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.Image_Serializers
