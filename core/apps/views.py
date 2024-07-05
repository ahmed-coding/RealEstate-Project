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
    """
    ViewSet for creating Feature_property instances with associated images.

    Example JSON payload:
    {
        "property": 1,
        "feature": 2,
        "feature_property_image": [
            {
                "image": "image1.jpg"
            },
            {
                "image": "image2.jpg"
            },
            {
                "image": "image3.jpg"
            }
        ]
    }

    Parameters:
    - property: The ID of the Property instance to which this Feature_property is related.
    - feature: The ID of the Feature instance to which this Feature_property is related.
    - feature_property_image: A list of image objects, where each object contains the image field representing the image file name or path.

    Note:
    - The IDs (property and feature) should correspond to existing instances in your database.
    - The image fields in feature_property_image should contain valid paths or names of the image files that will be processed by the ImageField.

    Attributes:
    - queryset: The queryset of Feature_property instances.
    - permission_classes: The list of permission classes that this viewset requires.
    - serializer_class: The serializer class that this viewset uses.
    """

    queryset = Feature_property.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.CreatePropertyfeaturedImage_Serializers


class CreatePropertyImageViewsets(viewsets.ModelViewSet):
    """
    ViewSet for creating Image instances associated with a Property.

    Example JSON payload:
    {
        "image": "image1.jpg",
        "object_id": 1
    }

    Parameters:
    - image: The image file name or path.
    - object_id: The ID of the Property instance to which this image is related.

    Note:
    - The object_id should correspond to an existing Property instance in your database.
    - The image field should contain a valid path or name of the image file that will be processed by the ImageField.

    Attributes:
    - queryset: The queryset of Property instances.
    - permission_classes: The list of permission classes that this viewset requires.
    - serializer_class: The serializer class that this viewset uses.
    """

    queryset = Property.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.CreatePropertyImage_Serializers
