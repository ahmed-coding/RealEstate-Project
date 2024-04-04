from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, action
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import filters

from ..models import Review
from ..pagination import StandardResultsSetPagination

from django_filters.rest_framework import DjangoFilterBackend
from . import serializers


class ReviewViewsets(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    search_fields = 'prop'
    serializer_class = serializers.ReviewSerializers
    lookup_field = ('prop',)
    filterset_fields = ['prop',]
    ordering_fields = '__all__'
    queryset = Review.objects.all()

    def get_queryset(self):
        prop = self.kwargs.get('prop')
        if prop:
            queryset = Review.objects.filter(prop=prop)
            if queryset.exists():
                return queryset
            else:
                return None
        return Review.objects.all()

    def get_serializer_context(self):
        return {'user': self.request.user}
