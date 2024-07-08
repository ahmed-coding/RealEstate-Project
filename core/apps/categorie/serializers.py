from rest_framework import serializers
from ..models import Category, Feature, Image, Attribute, Category_attribute, ValueModel


from ..serializers import Image_Serializers


class CategorySerializers(serializers.ModelSerializer):
    image = Image_Serializers(many=True, read_only=True)
    have_children = serializers.SerializerMethodField(read_only=True)

    def get_have_children(self, obj: Category) -> bool:

        return obj.get_children().exists()

    class Meta:
        model = Category
        fields = '__all__'


class ValueModelSerializers(serializers.ModelSerializer):

    class Meta:
        model = ValueModel
        fields = '__all__'


class AttributeSerializers(serializers.ModelSerializer):
    value_attribute = ValueModelSerializers(many=True, read_only=True)

    class Meta:
        model = Attribute
        fields = '__all__'


class AttributeByCategorieSerializers(serializers.ModelSerializer):
    category = CategorySerializers(read_only=True)
    attribute = AttributeSerializers(read_only=True)

    class Meta:
        model = Category_attribute
        fields = '__all__'


class FeatureByCategorySerializers(serializers.ModelSerializer):

    class Meta:
        model = Feature
        fields = ("id", "name")
