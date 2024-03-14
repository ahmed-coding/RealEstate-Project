from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import filters

from ..pagination import StandardResultsSetPagination
from rest_framework.views import Response

from apps.models import Category, Attribute, ValueModel, Category_attribute
from django_filters.rest_framework import DjangoFilterBackend

from . import serializers


class CategoryViewsets(viewsets.ModelViewSet):

    """CategoryViewsets

    Argament:
        parent: parent id to get all sup Categorie in `GET Method`
    """
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


class AttributeByCategorieViewsets(viewsets.ModelViewSet):

    """AttributeByCategorieViewsets

    Argament:
        category: categorie id to get all attribute in `GET Method` 
    """
    serializer_class = serializers.AttributeSerializers

    def get_queryset(self):
        category = self.request.query_params.get("category") or None
        return Attribute.objects.filter(category_attribute__category__id=category).order_by('id')
