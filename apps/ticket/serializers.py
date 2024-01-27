from rest_framework import serializers

from ..models import Ticket, Ticket_status, Ticket_type, Solve_message


class TicketSerializers(serializers.ModelSerializer):
    sender = serializers.HiddenField(default=None)

    def validate(self, attrs):
        sender = self.context.get('user' or None)
        attrs['sender'] = sender
        return super().validate(attrs)

    class Meta:
        model = Ticket
        fields = "__all__"


class TicketTypeSerilalizers(serializers.ModelSerializer):
    class Meta:
        model = Ticket_type
        fields = '__all__'


class TicketStatusSerializers(serializers.ModelSerializer):
    class Meta:

        model = Ticket_status
        fields = '__all__'
