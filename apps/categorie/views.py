from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import filters
from ..pagination import StandardResultsSetPagination
from rest_framework.views import Response

from apps.models import Category
from django_filters.rest_framework import DjangoFilterBackend

from . import serializers


class CategoryViewsets(viewsets.ModelViewSet):
    serializer_class = serializers.CategorySerializers
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', ]
    filterset_fields = ['name',]
    ordering_fields = '__all__'

    def get_queryset(self):
        parent = self.request.query_params.get("parent") or None
        return Category.objects.filter(parent=parent).order_by('id')
