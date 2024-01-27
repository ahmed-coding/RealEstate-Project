from rest_framework import serializers
from ..models import Category, Image

from ..serializers import Image_Serializers


class CategorySerializers(serializers.ModelSerializer):
    image = Image_Serializers(many=True, read_only=True)

    class Meta:
        model = Category
        fields = '__all__'
