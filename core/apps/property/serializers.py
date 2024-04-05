from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from ..serializers import Image_Serializers
from ..users.serializers import UserSerializer
from ..models import Address, Attribute, Image,  Property, Feature, Feature_property, User, property_value, ValueModel
from ..categorie.serializers import CategorySerializers
from ..address.serializers import AddressSerializers, CreateAddressSerializer
from ..review.serializers import ReviewSerializers

# class Image_Feature_propertySerializers(serializers.ModelSerializer):

#     class Meta:
#         model = Image
#         fiels = ('image',)


class propertyAddressSerializersI(AddressSerializers):
    def to_representation(self, instance):
        return instance.line1 if instance.line1.split(" ") != "" else instance.line2


class BastSellerSerializers(UserSerializer):
    """Bast Sellers

    Args:
        category (int): to get all sellers by categorys

    Returns:
        User: _description_
    """
    property_count = serializers.SerializerMethodField()

    def get_property_count(self, obj):
        return obj.property_count

    class Meta:
        fields = ['id', 'email', 'phone_number',
                  'username',   'name', 'is_active', 'image', 'property_count']
        model = User


class SinglePropertySerializers(serializers.ModelSerializer):
    rate_review = serializers.SerializerMethodField(read_only=True)
    in_favorite = serializers.SerializerMethodField(read_only=True)
    image = Image_Serializers(many=True, read_only=True)
    address = propertyAddressSerializersI(read_only=True)

    # review = ReviewSerializers(many=True, read_only=True)

    def get_in_favorite(self, obj) -> bool:
        user = self.context.get('user' or None)
        # if isinstance(user, User) else False
        return obj.favorites.filter(user=user).exists()

    # def get_rate(self, obj) -> float:
    #     # user = self.context.get('user' or None)
    #     rat = obj.rate.all()
    #     sub = 0.0
    #     if rat.exists():
    #         try:
    #             for s in rat:
    #                 sub += s.rate
    #             return round(sub / rat.count(), 1)
    #         except:
    #             sub = 0
    #             return round(sub, 1)
    #     else:
    #         return round(sub, 1)
    def get_rate_review(self, obj):
        ratings = obj.review.all().values_list('rate_review', flat=True)
        if ratings:
            average_rating = sum(ratings) / len(ratings)
            return round(average_rating, 1)
        else:
            return 0.0

    class Meta:
        model = Property
        fields = '__all__'


class FeatureSerializers(serializers.ModelSerializer):

    class Meta:
        model = Feature
        fields = '__all__'


class Feature_propertySerializers(serializers.ModelSerializer):
    feature = FeatureSerializers(read_only=True)
    image = Image_Serializers(many=True, read_only=True)

    class Meta:
        model = Feature_property
        fields = '__all__'


class AttributeVlaueSerializers(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = '__all__'


class ValueSerializers(serializers.ModelSerializer):
    attribute = AttributeVlaueSerializers(read_only=True)

    class Meta:
        model = ValueModel
        fields = '__all__'


class property_valueSerializers(serializers.ModelSerializer):
    value = ValueSerializers(read_only=True)

    class Meta:
        model = property_value
        fields = '__all__'


class PropertyDetailsSerializers(serializers.ModelSerializer):
    feature_property = Feature_propertySerializers(many=True, read_only=True)
    property_value = property_valueSerializers(many=True, read_only=True)
    rate_review = serializers.SerializerMethodField(read_only=True)
    in_favorite = serializers.SerializerMethodField(read_only=True)
    # address = propertyAddressSerializersI(read_only=True)
    address = AddressSerializers(read_only=True)
    category = CategorySerializers(read_only=True)
    user = UserSerializer(read_only=True)

    image = Image_Serializers(many=True, read_only=True)

    def get_in_favorite(self, obj) -> bool:
        user = self.context.get('user' or None)
        # if isinstance(user, User) else False
        return obj.favorites.filter(user=user).exists()

    # def get_rate_review(self, obj) -> float:
    #     # user = self.context.get('user' or None)
    #     rat = obj.review.all()
    #     sub = 0.0
    #     if rat.exists():
    #         try:
    #             for s in rat:
    #                 sub += s.review
    #             return round(sub / rat.count(), 1)
    #         except:
    #             sub = 0
    #             return round(sub, 1)
    #     else:
    #         return round(sub, 1)
    def get_rate_review(self, obj):
        ratings = obj.review.all().values_list('rate_review', flat=True)
        if ratings:
            average_rating = sum(ratings) / len(ratings)
            return round(average_rating, 1)
        else:
            return 0.0

    class Meta:
        model = Property
        fields = '__all__'


# Seller Method

# class CreatePropertySerializers(serializers.ModelSerializer):
#     """
#     Serializer class for creating a new property along with associated attribute values.

#     This serializer allows creating a new property along with attribute values in a single request.

#     Attributes:
#         attribute_values (dict): A dictionary containing attribute IDs as keys and their corresponding values.

#     Example Usage:
#         To create a property with attribute values:
#         ```
#         {
#             "user": 1,
#             "category": 1,
#             "address": 1,
#             "name": "Property Name",
#             "description": "Property Description",
#             "price": 100000,
#             "size": 2000,
#             "is_active": true,
#             "is_deleted": false,
#             "attribute_values": {
#                 "1": "Value1",
#                 "2": "Value2",
#                 "3": "Value3"
#             },
#             "for_sale": true
#         }
#         ```

#     Note:
#         Ensure that the attribute IDs provided in `attribute_values` exist in the database.
#     """
#     attribute_values = serializers.DictField(write_only=True)

#     def create(self, validated_data):
#         """
#         Create method for creating a new property with associated attribute values.

#         This method creates a new property instance along with its associated attribute values.

#         Args:
#             validated_data (dict): Validated data for creating the property.

#         Returns:
#             Property: The newly created property instance.
#         """
#         attribute_values_data = validated_data.pop('attribute_values', {})
#         property_instance = Property.objects.create(**validated_data)
#         for attribute_id, value in attribute_values_data.items():
#             attribute = Attribute.objects.get(id=attribute_id)
#             value_instance, _ = ValueModel.objects.get_or_create(
#                 attribute=attribute, value=value)
#             property_value.objects.create(
#                 property=property_instance, value=value_instance)
#         return property_instance

#     class Meta:
#         model = Property
#         fields = '__all__'


# class CreatePropertySerializer(serializers.ModelSerializer):
#     """
#     Serializer class for creating a new property along with associated address, features, and images.

#     This serializer allows creating a new property along with an address, features, and images in a single request.

#     Attributes:
#         address_data (dict): A dictionary containing address details.
#         feature_data (dict): A dictionary containing feature details.
#         image_data (list): A list of dictionaries containing image details.
#         attribute_values (dict): A dictionary containing attribute IDs as keys and their corresponding values.

#     Example Usage:
#         To create a property with address, features, and images:
#         ```
#         {
#             "user": 1,
#             "category": 1,
#             "name": "Property Name",
#             "description": "Property Description",
#             "price": 100000,
#             "size": 2000,
#             "is_active": true,
#             "is_deleted": false,
#             "attribute_values": {
#                 "1": "Value1",
#                 "2": "Value2",
#                 "3": "Value3"
#             },
#             "address_data": {
#                 "state": 1,
#                 "longitude": "longitude_value",
#                 "latitude": "latitude_value"
#             },
#             "feature_data": [
#                 {
#                 "name": "Feature Name"
#                 },
#                 {
#                 "name": "Feature Name"
#                 }
#             ],
#             "image_data": [
#                 {
#                     "image": "image_data"
#                 },
#                 {
#                     "image": "image_data"
#                 }
#             ],
#             "for_sale": true
#         }
#         ```

#     Note:
#         Ensure that the user and `category` IDs provided exist in the database.
#         Ensure that the attribute IDs provided in `attribute_values` exist in the database.

#     """
#     attribute_values = serializers.DictField(write_only=True)

#     address_data = CreateAddressSerializer()
#     feature_data = serializers.ListField(
#         child=serializers.DictField(), write_only=True)
#     image_data = serializers.ListField(
#         child=serializers.DictField(), write_only=True)

#     def create(self, validated_data):
#         address_data = validated_data.pop('address_data')
#         feature_data = validated_data.pop('feature_data', [])
#         image_data = validated_data.pop('image_data', [])
#         attribute_values_data = validated_data.pop('attribute_values', {})

#         address_instance = Address.objects.create(**address_data)
#         validated_data['address'] = address_instance
#         content_type = ContentType.objects.get_for_model(Property)
#         # Assuming 'id' is the ID of the property instance
#         property_instance = Property.objects.create(**validated_data)

#         object_id = property_instance.id
#         feature_instance = None
#         for feature in feature_data:
#             feature_instance = Feature.objects.create(**feature)
#             Feature_property.objects.create(
#                 property=property_instance, feature=feature_instance)

#         images_instances = []
#         for item in image_data:
#             item['content_type'] = content_type
#             item['object_id'] = object_id
#             image_instance = Image.objects.create(**item)
#             images_instances.append(image_instance)

#         for attribute_id, value in attribute_values_data.items():
#             attribute = Attribute.objects.get(id=attribute_id)
#             value_instance, _ = ValueModel.objects.get_or_create(
#                 attribute=attribute, value=value)
#             property_value.objects.create(
#                 property=property_instance, value=value_instance)

#         property_instance.image.set(images_instances)

#         return property_instance

#     class Meta:
#         model = Property
#         fields = '__all__'


class CreatePropertySerializer(serializers.ModelSerializer):
    """
    Serializer class for creating a new property along with associated address, features, and images.

    This serializer allows creating a new property along with an address, features, and images in a single request.

    Attributes:
        address_data (dict): A dictionary containing address details.
        feature_data (list): A list of dictionaries containing feature details.
        attribute_values (dict): A dictionary containing attribute IDs as keys and their corresponding values.
        image_data (list): A list of dictionaries containing image details.


    Example Usage:
        To create a property with address, features, and images:
        ```
    {

        "category": 1,
        "name": "Property Name",
        "description": "Property Description",
        "price": 100000,
        "size": 2000,
        "is_active": true,
        "is_deleted": false,
        "attribute_values": {
            "1": "Value1",
            "2": "Value2",
            "3": "Value3"
        },
        "address": {
            "state": 1,
            "longitude": "20.354654",
            "latitude": "32.354654"
        },
        "feature_data": [
            {
                "id": 1,
                "images": [
                    {
                        "image": "image_data"
                    },
                    {
                        "image": "image_data"
                    }
                ]
            },
            {
                "id": 2,
                "images": [
                    {
                        "image": "image_data"
                    },
                    {
                        "image": "image_data"
                    }
                ]
            }
        ],
        "image_data": [
            {
                "image": "image_data"
            },
            {
                "image": "image_data"
            }
        ],
        "for_sale": true
    }

        ```

    Note:
        Ensure that the user and `category` IDs provided exist in the database.
        Ensure that the attribute IDs provided in `attribute_values` exist in the database.

    """
    user = serializers.HiddenField(default=None)

    attribute_values = serializers.DictField(write_only=True)
    address = CreateAddressSerializer()
    feature_data = serializers.ListField(
        child=serializers.DictField(), write_only=True)
    image_data = serializers.ListField(
        child=serializers.DictField(), write_only=True)

    def validate(self, attrs):
        attrs['user'] = self.context.get('user', None)
        # self.address.context = self.context
        return super().validate(attrs)

    def create(self, validated_data):
        address_data = validated_data.pop('address')
        feature_data = validated_data.pop('feature_data', [])
        attribute_values_data = validated_data.pop('attribute_values', {})
        image_data = validated_data.pop('image_data', [])

        address_instance = Address.objects.create(**address_data)
        validated_data['address'] = address_instance
        content_type = ContentType.objects.get_for_model(Property)
        # Assuming 'id' is the ID of the property instance
        property_instance = Property.objects.create(**validated_data)

        object_id = property_instance.id

        # Create features and associated images
        for feature_item in feature_data:
            images_data = feature_item.pop('images', [])
            feature_instance = Feature.objects.get(id=feature_item['id'])
            feature_property = Feature_property.objects.create(
                property=property_instance, feature=feature_instance)

            feature_images_instances = []
            for image_data in images_data:
                image_data['content_type'] = ContentType.objects.get_for_model(
                    Feature_property)
                image_data['object_id'] = feature_property.id
                image_instance = Image.objects.create(**image_data)
                feature_images_instances.append(feature_images_instances)
            feature_property.image.set(feature_images_instances)

        images_instances = []
        for item in image_data:
            item['content_type'] = content_type
            item['object_id'] = object_id
            image_instance = Image.objects.create(**item)
            images_instances.append(image_instance)

        # Create attribute values
        for attribute_id, value in attribute_values_data.items():
            attribute = Attribute.objects.get(id=attribute_id)
            value_instance, _ = ValueModel.objects.get_or_create(
                attribute=attribute, value=value)
            property_value.objects.create(
                property=property_instance, value=value_instance)

        property_instance.image.set(images_instances)

        return property_instance

    class Meta:
        model = Property
        fields = '__all__'
