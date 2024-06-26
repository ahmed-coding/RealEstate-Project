from rest_framework.decorators import api_view, action
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import filters
from ..pagination import StandardResultsSetPagination
from rest_framework.views import Response

from apps.models import State, Country, City, Address
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from . import serializers


class CountryViewsets(viewsets.ModelViewSet):
    """_summary_

    Args:
        viewsets (_type_): _description_
    """
    serializer_class = serializers.CountrySerializers
    queryset = Country.objects.all().order_by('-id')


class CityViewsets(viewsets.ModelViewSet):
    """CityViewsets

    Argament:
        `country`: country id to get all City in `GET Method`
    """
    serializer_class = serializers.CitySerializers
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'country']
    ordering_fields = '__all__'
    filterset_fields = ['name', 'country', ]

    def get_queryset(self):
        country = self.request.query_params.get("country") or None
        if country:
            return City.objects.filter(country=country).order_by('id')
        else:
            return City.objects.all().order_by('id')


class StateViewsets(viewsets.ModelViewSet):
    """StateViewsets

    Argament:
        - `city`: city id to get all State in `GET Method`
        - `main_category`: Main category id to get all State in `GET Method`
    """
    serializer_class = serializers.StateSerializers
    # pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'city']
    ordering_fields = '__all__'
    filterset_fields = ['name', 'city', ]

    def get_queryset(self):
        city = self.request.query_params.get("city") or None
        category_id = self.request.query_params.get("main_category")
        category_id = None if category_id == '0' else category_id

        # If category_id is provided, filter states based on properties in that category
        queryset = State.objects.all().order_by('id')
        if category_id:
            queryset = queryset.filter(
                addresses__property__category__parent__id=category_id
            ).distinct().order_by('id')
        if city:
            queryset = queryset.filter(city=city).order_by('id')
        return queryset


class AddressViewsets(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.CreateAddressSerializer

    # def list(self, request):
    #     addresses = self.queryset
    #     serializer = self.serializer_class(addresses, many=True)
    #     return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
