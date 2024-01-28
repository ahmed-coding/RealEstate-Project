from rest_framework import serializers
from ..models import Address, City, Country, State


class CountrySerializers(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class CitySerializers(serializers.ModelSerializer):
    country = CountrySerializers(read_only=True)

    class Meta:
        model = City
        fields = '__all__'


class StateSerializers(serializers.ModelSerializer):
    city = CitySerializers(read_only=True)

    class Meta:
        model = State
        fields = '__all__'


class AddressSerializers(serializers.ModelSerializer):
    state = StateSerializers(read_only=True)

    class Meta:
        model = Address
        fields = '__all__'
