from .models import Feature_property, Image, Property
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType


class Image_Serializers(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ("image", "id")

    # def to_representation(self, instance):
    #     return instance.image.url


class CreatePropertyfeaturedImage_Serializers(serializers.ModelSerializer):
    feature_property_image = Image_Serializers(many=True, required=False)

    class Meta:
        model = Feature_property
        fields = "__all__"

    def create(self, validated_data):
        images_data = validated_data.pop('feature_property_image', [])
        feature_property_instance = Feature_property.objects.create(
            **validated_data)
        content_type = ContentType.objects.get_for_model(Feature_property)
        for image_data in images_data:
            Image.objects.create(object_id=feature_property_instance.id,
                                 content_type=content_type, image=image_data['image'])
        return feature_property_instance

    # def to_representation(self, instance):
    #     return instance.image.url


class CreatePropertyImage_Serializers(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = fields = ("image", "object_id", "id")

    def validate(self, attrs):
        attrs['content_type'] = ContentType.objects.get_for_model(
            Property)
        return super().validate(attrs)
    # def create(self, validated_data):
    #     images_data = validated_data.pop('feature_property_image', [])
    #     feature_property_instance = Feature_property.objects.create(
    #         **validated_data)
    #     content_type = ContentType.objects.get_for_model(Feature_property)
    #     for image_data in images_data:
    #         Image.objects.create(object_id=feature_property_instance.id,
    #                              content_type=content_type, image=image_data['image'])
    #     return feature_property_instance
