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
from rest_framework.views import Response


class ReviewViewsets(viewsets.ModelViewSet):
    """Review Viewsets

    Args:
        (max_rate_review): to get all review by max rate
        (min_rate_review): to get all review by min rate
    Usege:
    it's used togther to get review in range like `?min_rate_review=1&max_rate_review=2`


    Returns:
        queryset: Review queryset
    """
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    search_fields = 'prop'
    serializer_class = serializers.ReviewSerializers
    lookup_field = ('pkprop',)
    filterset_fields = ['prop', 'rate_review']
    ordering_fields = '__all__'
    queryset = Review.objects.all()

    def get_queryset(self):
        # withowt min and max rate
        # prop = self.kwargs.get('pkprop', None) or None

        # queryset = Review.objects.filter(prop=prop)
        # #     if queryset.exists():
        # #         print(queryset)
        # #         return queryset

        # #     else:
        # #         # return Response({'error': 'Ther is no review for this proprety.'}, status=status.HTTP_400_BAD_REQUEST)
        # #         return queryset

        # # else:
        # #     return Review.objects.all()
        # return queryset

        prop = self.kwargs.get('pkprop', None) or None
        max_rate = self.request.query_params.get('max_rate_review', None)
        min_rate = self.request.query_params.get('min_rate_review', None)

        queryset = Review.objects.filter(prop=prop)

        if max_rate is not None:
            queryset = queryset.filter(rate_review__lte=max_rate)

        if min_rate is not None:
            queryset = queryset.filter(rate_review__gte=min_rate)

        return queryset

    def get_serializer_context(self):
        return {'user': self.request.user}
    
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)  # Assign the current user to the review
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
