from django.db.models import Count, Case, When, IntegerField
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import filters
from ..pagination import StandardResultsSetPagination
from rest_framework.views import Response
from ..models import Property, User
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Q
from . import serializers
from rest_framework import generics


class AlarmViewsets(viewsets.ModelViewSet):
    serializer_class = serializers.CreateAlarmSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = '__all__'
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
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
        return super().create(request, *args, **kwargs)

    def get_serializer_context(self):
        return {
            "request": self.request,
            "format": self.format_kwarg,
            "view": self,
            "user": self.request.user,
        }
