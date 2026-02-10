from rest_framework import serializers
from ..models import Alarm, Alarm_value


class CreateAlarmSerializer(serializers.ModelSerializer):
    """Creates a new alarm along with associated alarm values.
    Example Request Body:
    ```
        {
            "state": 1,
            "category": 1,
            "is_active": true,
            "max_price": 100000,
            "min_price": 50000,
            "for_sale": true,
            "for_rent": false,
            "alarm_values": [
                {
                    "attribute_id": 1,
                    "value": "3"
                },
                {
                    "attribute_id": 2,
                    "value": "200.5"
                },
                {
                    "attribute_id": 3,
                    "value": "true"
                }
            ]
        }
    ```
    """

    alarm_values = serializers.ListField(
        child=serializers.DictField(), default=[{}])
    user = serializers.HiddenField(default=None)

    class Meta:
        model = Alarm
        fields = '__all__'

    def validate(self, attrs):
        attrs['user'] = self.context.get('user', None)
        # self.address.context = self.context
        return super().validate(attrs)

    def create(self, validated_data):
        alarm_values_data = validated_data.pop('alarm_values', [])
        alarm = Alarm.objects.create(**validated_data)
        for alarm_value_data in alarm_values_data:
            if 'attribute_id' in alarm_value_data and 'value' in alarm_value_data:
                attribute_id = alarm_value_data.pop('attribute_id')
                value = alarm_value_data.pop('value')
                Alarm_value.objects.create(
                    alarm=alarm, attribute_id=attribute_id, value=value)
        return alarm
