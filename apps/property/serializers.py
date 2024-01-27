from rest_framework import serializers

from ..serializers import Image_Serializers
from ..users.serializers import UserSerializer
from ..models import Attribute, Image,  Property, Feature, Feature_property, property_value, ValueModel
from ..categorie.serializers import CategorySerializers
from ..address.serializers import AddressSerializers
from ..review.serializers import ReviewSerializers

# class Image_Feature_propertySerializers(serializers.ModelSerializer):

#     class Meta:
#         model = Image
#         fiels = ('image',)


class SinglePropertySerializers(serializers.ModelSerializer):
    rate = serializers.SerializerMethodField(read_only=True)
    in_favorite = serializers.SerializerMethodField(read_only=True)
    image = Image_Serializers(many=True, read_only=True)
    # review = ReviewSerializers(many=True, read_only=True)

    def get_in_favorite(self, obj) -> bool:
        user = self.context.get('user' or None)
        # if isinstance(user, User) else False
        return obj.favorites.filter(user=user).exists()

    def get_rate(self, obj):
        # user = self.context.get('user' or None)
        rat = obj.rate.all()
        sub = 0.0
        if rat.exists():
            try:
                for s in rat:
                    sub += s.rate
                return round(sub / rat.count(), 1)
            except:
                sub = 0
                return round(sub, 1)
        else:
            return round(sub, 1)

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


class AttributeSerializers(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = '__all__'


class ValueSerializers(serializers.ModelSerializer):
    attribute = AttributeSerializers(read_only=True)

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
    rate = serializers.SerializerMethodField(read_only=True)
    in_favorite = serializers.SerializerMethodField(read_only=True)
    address = AddressSerializers(read_only=True)
    category = CategorySerializers(read_only=True)
    user = UserSerializer(read_only=True)
    image = Image_Serializers(many=True, read_only=True)

    def get_in_favorite(self, obj) -> bool:
        user = self.context.get('user' or None)
        # if isinstance(user, User) else False
        return obj.favorites.filter(user=user).exists()

    def get_rate(self, obj):
        # user = self.context.get('user' or None)
        rat = obj.rate.all()
        sub = 0.0
        if rat.exists():
            try:
                for s in rat:
                    sub += s.rate
                return round(sub / rat.count(), 1)
            except:
                sub = 0
                return round(sub, 1)
        else:
            return round(sub, 1)

    class Meta:
        model = Property
        fields = '__all__'
