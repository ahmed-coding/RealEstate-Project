from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import filters

from ..pagination import StandardResultsSetPagination
from rest_framework.views import Response

from apps.models import Banner
from django_filters.rest_framework import DjangoFilterBackend

from . import serializers


class BannerViewSetst(viewsets.ModelViewSet):
    serializer_class = serializers.BannerSerializers
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', ]
    filterset_fields = ['title',]
    ordering_fields = '__all__'
    queryset = Banner.objects.all()
