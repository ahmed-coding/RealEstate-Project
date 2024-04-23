from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

# from apps.cart.serializers import CreateFavoriteSerializers
from ..pagination import StandardResultsSetPagination
from rest_framework.views import Response

from ..models import Favorite,  Review, Ticket, Ticket_type, User
from . import serializers


class TicketViewsets(viewsets.ModelViewSet):
    # queryset = Ticket_type
    # serializer_class = serializers.TicketTypeSerilalizers
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.action == 'list':
            return Ticket_type.objects.all()
        else:
            return Ticket.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.TicketTypeSerilalizers
        else:
            return serializers.TicketSerializers

    def get_serializer_context(self):
        user = self.request.user if isinstance(
            User, self.request.user) else None
        return {'user': user}

    # @action(detail=True, methods=['list'])
    # def get_ticket_type(self, request, *args, **kwargs):
    #     ser = self.get_serializer_class()

    #     ser = ser()
