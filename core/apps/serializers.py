from .models import Feature_property, Image, Property
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType


class Image_Serializers(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ("image","id")

    # def to_representation(self, instance):
    #     return instance.image.url


class CreatePropertyfeaturedImage_Serializers(serializers.ModelSerializer):
    # images = Image_Serializers(many=True, required=False)

    image = serializers.ImageField()  # Use ImageField to handle file uploads

    class Meta:
        model = Feature_property
        fields = ['property', 'feature', 'image']

    def create(self, validated_data):
        image_file = validated_data.pop('image')
        feature_property_instance = Feature_property.objects.create(**validated_data)
        
        Image.objects.create(content_object=feature_property_instance, image=image_file)
        
        return feature_property_instance
    # class Meta:
    #     model = Feature_property
    #     fields = "__all__"

    # def create(self, validated_data):
    #     """
    #     Create a Feature_property instance and associated images.

    #     Example JSON payload:
    #     {
    #         "property": 1,
    #         "feature": 2,
    #         "image": "image3.jpg"
    #     }

    #     Parameters:
    #     validated_data (dict): The validated data from the serializer.

    #     Returns:
    #     Feature_property: The created Feature_property instance with associated images.

    #     Explanation of JSON Fields:
    #     - property: The ID of the Property instance to which this Feature_property is related.
    #     - feature: The ID of the Feature instance to which this Feature_property is related.
    #     - feature_property_image: A list of image objects, where each object contains the image field representing the image file name or path.

    #     Note:
    #     - The IDs (property and feature) should correspond to existing instances in your database.
    #     - The image fields in feature_property_image should contain valid paths or names of the image files that will be processed by the ImageField.
    #     """
    #     image_data = validated_data.pop('image')
    #     feature_property_instance = Feature_property.objects.create(**validated_data)
        
    #     Image.objects.create(feature_property=feature_property_instance, image=image_data)
        
    #     return feature_property_instance

    # def to_representation(self, instance):
    #     return instance.image.url


class CreatePropertyImage_Serializers(serializers.ModelSerializer):
    """
    Serializer for creating Image instances associated with a Property.

    Example JSON payload:
    {
        "image": "image1.jpg",
        "object_id": 1
    }

    Parameters:
    validated_data (dict): The validated data from the serializer.

    Returns:
    Image: The created Image instance.

    Explanation of JSON Fields:
    - image: The image file name or path.
    - object_id: The ID of the Property instance to which this image is related.

    Note:
    - The object_id should correspond to an existing Property instance in your database.
    - The image field should contain a valid path or name of the image file that will be processed by the ImageField.
    """
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
