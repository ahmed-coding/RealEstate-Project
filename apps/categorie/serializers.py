from rest_framework import serializers
from ..models import Category, Image_Category


class Image_CategorySerializers(serializers.ModelSerializer):

    class Meta:
        model = Image_Category
        fields = ('image',)


class CategorySerializers(serializers.ModelSerializer):
    image = Image_CategorySerializers(many=True, read_only=True)

    class Meta:
        model = Category
        fields = '__all__'
