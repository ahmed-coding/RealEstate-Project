from rest_framework.decorators import api_view, action
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import filters
from ..pagination import StandardResultsSetPagination
from rest_framework.views import Response

from apps.models import State
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from . import serializers


class StateViewsets(viewsets.ModelViewSet):
    serializer_class = serializers.StateSerializers
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', ]
    filterset_fields = ['name',]
    ordering_fields = '__all__'
    queryset = State.objects.all().order_by('-id')
