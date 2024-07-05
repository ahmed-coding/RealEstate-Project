from django.shortcuts import render
from rest_framework import viewsets
from apps.models import Image, Feature_property, Property
from . import serializers
from rest_framework.permissions import IsAuthenticated

# Create your views here.


class ImageViewsets(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.Image_Serializers

    def get_serializer_class(self):
        if self.action == "create":
            print(self.request.data)
            return serializers.CreatePropertyfeaturedImage_Serializers
        return super().get_serializer_class()


class CreatePropertyfeaturedImageViewsets(viewsets.ModelViewSet):
    """Create Property feature Image Viewsets
    """
    queryset = Feature_property.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.CreatePropertyfeaturedImage_Serializers


class CreatePropertyImageViewsets(viewsets.ModelViewSet):
    """Create Property Image Viewsets
    """
    queryset = Property.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.CreatePropertyImage_Serializers
