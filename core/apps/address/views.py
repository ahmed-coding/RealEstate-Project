from rest_framework.decorators import api_view, action
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import filters
from ..pagination import StandardResultsSetPagination
from rest_framework.views import Response

from apps.models import State, Country, City
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from . import serializers


class CountryViewsets(viewsets.ModelViewSet):
    serializer_class = serializers.CountrySerializers
    queryset = Country.objects.all().order_by('-id')


class CityViewsets(viewsets.ModelViewSet):
    """CityViewsets

    Argament:
        country: country id to get all City in `GET Method`
    """
    serializer_class = serializers.CitySerializers

    def get_queryset(self):
        country = self.request.query_params.get("country") or None
        if country:
            return City.objects.filter(country=country).order_by('id')
        else:
            return City.objects.all().order_by('id')


class StateViewsets(viewsets.ModelViewSet):
    """StateViewsets

    Argament:
        city: city id to get all State in `GET Method`
    """
    serializer_class = serializers.StateSerializers
    # pagination_class = StandardResultsSetPagination
    # filter_backends = [DjangoFilterBackend,
    #                    filters.SearchFilter, filters.OrderingFilter]
    # search_fields = ['name', ]
    # filterset_fields = ['name',]
    ordering_fields = '__all__'

    def get_queryset(self):
        city = self.request.query_params.get("city") or None
        if city:
            return State.objects.filter(city=city).order_by('id')
        else:
            return State.objects.all().order_by('id')
