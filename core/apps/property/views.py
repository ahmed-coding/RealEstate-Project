from rest_framework.filters import OrderingFilter
from django.db.models import Count, Case, When, IntegerField
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import filters
from ..pagination import StandardResultsSetPagination
from rest_framework.views import Response
from ..models import Property, User
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Q
from . import serializers
from rest_framework import generics


class BastSellerViewsets(viewsets.ModelViewSet):
    """BastSellerViewsets

    Args:
        - `category`: for get all Sellers from `Main Category` in `GET` method 
        - `user_type`: for get all Sellers By `user_type` in `GET` method
        - `user_type-choices`: `owner`, `agent`, `promoter`

    """
    serializer_class = serializers.BastSellerSerializers
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', ]
    filterset_fields = ['name',]
    ordering_fields = '__all__'
    # queryset = User.objects.annotate(
    #     property_count=Count('property')
    # ).filter(is_seller=True).order_by('-property_count')

    def get_queryset(self):
        category = self.request.query_params.get(
            "category", None) or None
        user_type = self.request.query_params.get(
            "user_type", None) or None
        # queryset = User.objects.annotate(
        #     property_count=Count(
        #         Case(
        #             When(property__category_id=category, then=1),
        #             output_field=IntegerField(),
        #         )
        #     )
        # ).filter(is_seller=True).order_by('-property_count')
        # queryset = User.objects.annotate(
        #     property_count=Count('property', filter=Q(
        #         property__category=category))
        # ).order_by('-property_count')
        if category:
            queryset = User.objects.filter(
                property__category__parent__id=category, is_seller=True, user_type__in=["owner", "agent", "promoter"]).annotate(
                property_count=Count('property', filter=Q(
                    property__category=category))
            ).order_by('-property_count')
        else:
            queryset = User.objects.filter(
                is_seller=True, user_type__in=["owner", "agent", "promoter"]).annotate(
                property_count=Count('property')
            ).order_by('-property_count')
        if user_type:
            queryset = queryset.filter(user_type=user_type)
        return queryset


class PropertyViewsets(viewsets.ModelViewSet):
    """Property Viewsets
    Args:
        - main_category: for get all property from Main Category in GET method from two levels
        - state: state id for get all property in that state.
    """
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    filterset_fields = ['name', 'is_featured', 'category', 'user', 'is_active']
    ordering_fields = 'all'
    # Description of params
    main_category = None
    main_category_query_param = 'main_category'
    main_category_query_description = _(
        "for get all property from Main Category in GET method from two levels")

    def get_serializer_context(self):
        return {'user': self.request.user} if self.request.user.is_authenticated else {}

    def get_queryset(self):
        self.main_category = self.request.query_params.get(
            "main_category", None)
        is_active = self.request.query_params.get("is_active", None)

        queryset = Property.objects.all()

        if self.main_category:
            queryset = queryset.filter(category__parent__id=self.main_category)

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        if self.action == 'get_high_rate':
            return queryset.annotate(
                rating_count=Count('rate')
            ).order_by('-rating_count')
        elif self.action == 'get_by_address':
            pk = self.kwargs.get('pk')
            obj = Property.objects.get(id=pk)
            return queryset.filter(address__state=obj.address.state).exclude(id=pk).order_by('-id')
        elif self.action == 'get_by_state':
            state = self.request.query_params.get("state", None)
            return queryset.filter(address__state=state).order_by('-id')
        else:
            return queryset.order_by('-id')

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
            serializer.data
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
            serializer.data
        })

    @action(detail=True, methods=['list'])
    def get_by_state(self, request, *args, **kwargs):
        """State Viewsets
        Args:
            - `state`: state id for get all property in that `state`.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            serializer.data
        })


class PropertyCreateAPIView(viewsets.ModelViewSet):
    """
    API view class for creating a new property along with address and images.

    This view class provides an endpoint for creating a new property along with associated address and images.

    Example Usage:
        To create a property with address, features, and images:
        ```
        {

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

    def get_queryset(self):
        # if self.action == 'partial_update':
        #     return Property.objects.filter(user=self.request.user)
        return Property.objects.filter(user=self.request.user)

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


class PropertyFilterViewSet(viewsets.ModelViewSet):
    """
    Viewset for filtering the Property model.

    Filtering Parameters:
        state: Filter by state (e.g., ?state=5)
        category: Filter by category ID (e.g., ?category=1)
        max_price: Filter properties with price less than or equal to the given value (e.g., ?max_price=100000)
        min_price: Filter properties with price greater than or equal to the given value (e.g., ?min_price=50000)
        for_sale: Filter properties that are for sale (e.g., ?for_sale=true)
        for_rent: Filter properties that are for rent (e.g., ?for_rent=true)
        attribute_value: Filter properties by attribute value (e.g., ?attribute_value=Sea View)

    Ordering Parameters:
        price: Order by price (e.g., ?ordering=price or ?ordering=-price for descending)
        time_created: Order by creation time (e.g., ?ordering=time_created or ?ordering=-time_created for descending)

    Args:
        viewsets.ModelViewSet: A base class for all viewsets that provides default CRUD operations.

    Returns:
        QuerySet: The filtered and ordered queryset of Property objects.

    Example JSON payload:
    {
        "state": "California",
        "category": 1,
        "max_price": 100000,
        "min_price": 50000,
        "for_sale": true,
        "for_rent": false,
        "attribute_values": [
            {
                "attribute_id": 1,
                "value": "3"
            },
            {
                "attribute_id": 2,
                "value": "200.5"
            },
            {
                "attribute_id": 3,
                "value": "true"
            }
        ]
    }
    """
    # queryset = Property.objects.all()
    serializer_class = serializers.PropertyFilterSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['category', 'for_sale', 'for_rent']
    ordering_fields = ['price', 'time_created']

    def get_queryset(self):
        queryset = Property.objects.all()

        state = self.request.query_params.get("state", None)
        category = self.request.query_params.get('category', None)
        # is_active = data.get('is_active')
        max_price = self.request.query_params.get('max_price', None)
        min_price = self.request.query_params.get('min_price', None)
        for_sale = self.request.query_params.get('for_sale', None)
        for_rent = self.request.query_params.get('for_rent', None)
        attribute_values = self.request.query_params.get(
            'attribute_values', [])

        if state:
            queryset = queryset.filter(address__state=state)

        if category:
            queryset = queryset.filter(category=category)

        # if is_active is not None:
        #     queryset = queryset.filter(is_active=is_active)

        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)

        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)

        if for_sale is not None:
            queryset = queryset.filter(for_sale=for_sale)

        if for_rent is not None:
            queryset = queryset.filter(for_rent=for_rent)

        for attribute in attribute_values:
            attribute_id = attribute.get('attribute_id')
            value = attribute.get('value')
            if attribute_id and value:
                queryset = queryset.filter(
                    property_value__attribute_id=attribute_id, property_value__value=value)

        return queryset

    # @action(detail=False, methods=['post'])
    # def filter(self, request):
    #     """
    #     Custom action to filter properties based on JSON payload.

    #     Returns:
    #         Response: A list of filtered Property objects.
    #     """
    #     queryset = self.get_queryset()
    #     data = request.data

    #     state = data.get('state')
    #     category = data.get('category')
    #     # is_active = data.get('is_active')
    #     max_price = data.get('max_price')
    #     min_price = data.get('min_price')
    #     for_sale = data.get('for_sale')
    #     for_rent = data.get('for_rent')
    #     attribute_values = data.get('attribute_values', [])

    #     if state:
    #         queryset = queryset.filter(address__state=state)

    #     if category:
    #         queryset = queryset.filter(category=category)

    #     # if is_active is not None:
    #     #     queryset = queryset.filter(is_active=is_active)

    #     if max_price is not None:
    #         queryset = queryset.filter(price__lte=max_price)

    #     if min_price is not None:
    #         queryset = queryset.filter(price__gte=min_price)

    #     if for_sale is not None:
    #         queryset = queryset.filter(for_sale=for_sale)

    #     if for_rent is not None:
    #         queryset = queryset.filter(for_rent=for_rent)

    #     for attribute in attribute_values:
    #         attribute_id = attribute.get('attribute_id')
    #         value = attribute.get('value')
    #         if attribute_id and value:
    #             queryset = queryset.filter(
    #                 property_value__attribute_id=attribute_id, property_value__value=value)

    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)
