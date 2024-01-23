from rest_framework.decorators import api_view, action
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import filters
from ..pagination import StandardResultsSetPagination
from rest_framework.views import Response

from apps.models import User
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from . import serializers


class BastSellerViewsets(viewsets.ModelViewSet):
    serializer_class = serializers.PropertySerializers
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', ]
    filterset_fields = ['name',]
    ordering_fields = '__all__'
    queryset = User.objects.annotate(
        property_count=Count('property')
    ).filter(is_seller=True).order_by('-property_count')
