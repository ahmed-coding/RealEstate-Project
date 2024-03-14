from rest_framework import serializers
from ..models import Address, City, Country, State


class StateSerializers(serializers.ModelSerializer):

    class Meta:
        model = State
        fields = '__all__'


class CitySerializers(serializers.ModelSerializer):
    state = StateSerializers(many=True, read_only=True)

    class Meta:
        model = City
        fields = '__all__'


class CountrySerializers(serializers.ModelSerializer):
    city = CitySerializers(many=True, read_only=True)

    class Meta:
        model = Country
        fields = '__all__'


class AddressSerializers(serializers.ModelSerializer):
    state = StateSerializers(read_only=True)

    class Meta:
        model = Address
        fields = '__all__'
