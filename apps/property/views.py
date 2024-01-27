from rest_framework.decorators import api_view, action
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import filters
from ..pagination import StandardResultsSetPagination
from rest_framework.views import Response

from apps.models import Property
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg
from . import serializers


class PropertyViewsets(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', ]
    filterset_fields = ['name',]
    ordering_fields = '__all__'

    def get_serializer_context(self):
        return {'user': self.request.user} if self.request.user.is_authenticated else {}

    def get_queryset(self):
        if self.action == 'get_high_rate':
            return Property.objects.annotate(
                rating_count=Count('rate')
            ).order_by('-rating_count')
        elif self.action == 'get_by_address':
            pk = self.kwargs.get('pk')
            obj = Property.objects.get(id=pk)
            return Property.objects.filter(address__state=obj.address.state).exclude(id=pk).order_by('-id')
        else:
            return Property.objects.all().order_by('-id')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.PropertyDetailsSerializers
        else:
            return serializers.SinglePropertySerializers

    @action(detail=True, methods=['list'])
    def get_high_rate(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'data': serializer.data
        })

    @action(detail=True, methods=['list'])
    def get_by_address(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'data': serializer.data
        })
