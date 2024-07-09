from rest_framework import serializers


class PropertyPricePredictSerializers(serializers.Serializer):
    query = serializers.IntegerField()
    price = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False)
