from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import filters
from ..pagination import StandardResultsSetPagination
from rest_framework.views import Response

from ..models import Property, User
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg
from . import serializers
from rest_framework import generics


class BastSellerViewsets(viewsets.ModelViewSet):
    serializer_class = serializers.PropertyDetailsSerializers
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', ]
    filterset_fields = ['name',]
    ordering_fields = '__all__'
    queryset = User.objects.annotate(
        property_count=Count('property')
    ).filter(is_seller=True).order_by('-property_count')


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


class PropertyCreateAPIView(generics.CreateAPIView):
    """
    API view class for creating a new property along with address and images.

    This view class provides an endpoint for creating a new property along with associated address and images.

    Example Usage:
        To create a property with address, features, and images:
        ```
        {

        "user": 1,
        "category": 1,
        "name": "Property Name",
        "description": "Property Description",
        "price": 100000,
        "size": 2000,
        "is_active": true,
        "is_deleted": false,
        "attribute_values": {
            "1": "Value1",
            "2": "Value2",
            "3": "Value3"
        },
        "address": {
            "state": 1,
            "longitude": "20.354654",
            "latitude": "32.354654"
        },
        "feature_data": [
            {
                "id": 1,
                "images": [
                    {
                        "image": "image_data"
                    },
                    {
                        "image": "image_data"
                    }
                ]
            },
            {
                "id": 2,
                "images": [
                    {
                        "image": "image_data"
                    },
                    {
                        "image": "image_data"
                    }
                ]
            }
        ],
        "image_data": [
            {
                "image": "image_data"
            },
            {
                "image": "image_data"
            }
        ],
        "for_sale": true
    }
        ```

    Note:
        Ensure that the user and `category` IDs provided exist in the database.
        Ensure that the attribute IDs provided in `attribute_values` exist in the database.


    """
    serializer_class = serializers.CreatePropertySerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
            'user': self.request.user
        }
