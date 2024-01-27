from sqlite3 import IntegrityError
from apps.models import Favorite,  Rate, Review, Category, User
from rest_framework import serializers

from ..property.serializers import SinglePropertySerializers
# from ..orders.serializers import Order_itemSerializers, OrderSerializers


class FavoriteSerializers(serializers.ModelSerializer):
    user = serializers.HiddenField(default=None)
    prop = SinglePropertySerializers(read_only=True)

    def validate(self, attrs):
        # self.user = self.context.get('user').id
        self.prop.context = self.context
        attrs['user'] = self.context.get('user')
        return super().validate(attrs)

    class Meta:
        model = Favorite
        fields = '__all__'


class CreateFavoriteSerializers(serializers.ModelSerializer):
    # user = serializers.HiddenField(default=None)
    # product = ProductSerializer(many=True, read_only=True)
    # prop = serializers.IntegerField()

    def validate(self, attrs):
        # self.user = self.context.get('user').id
        attrs['user'] = self.context.get('user')
        return super().validate(attrs)

    # def create(self, validated_data):
    #     user = self.context['user']
    #     product_id = validated_data['product']
    #     favorite, created = Favorite.objects.get_or_create(
    #         user=user, product_id=product_id)
    #     return favorite

    class Meta:
        model = Favorite
        fields = ('prop',)
