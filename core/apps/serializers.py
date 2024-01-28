from .models import Image
from rest_framework import serializers


class Image_Serializers(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ("image",)

    def to_representation(self, instance):
        return instance.image.url
