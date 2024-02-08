from rest_framework import serializers
from ..models import Category, Image

from ..serializers import Image_Serializers


class CategorySerializers(serializers.ModelSerializer):
    image = Image_Serializers(many=True, read_only=True)
    have_children = serializers.SerializerMethodField(read_only=True)

    def get_have_children(self, obj: Category) -> bool:

        return obj.get_children().exists()

    class Meta:
        model = Category
        fields = '__all__'
