from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import filters
from django.utils import timezone

from ..pagination import StandardResultsSetPagination
from rest_framework.views import Response

from apps.models import Banner
from django_filters.rest_framework import DjangoFilterBackend

from . import serializers


class BannerViewSetst(viewsets.ModelViewSet):
    serializer_class = serializers.BannerSerializers
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', ]
    filterset_fields = ['title', 'category']
    ordering_fields = '__all__'
    queryset = Banner.objects.filter(is_active=True)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Ensure end_time is not in the past
            end_time = serializer.validated_data.get('end_time')
            if end_time and end_time < timezone.now():
                return Response({'error': 'End time cannot be in the past.'}, status=status.HTTP_400_BAD_REQUEST)

            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
