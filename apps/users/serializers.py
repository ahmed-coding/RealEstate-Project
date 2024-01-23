from rest_framework import serializers
from ..models import State


class StateSerializers(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'
