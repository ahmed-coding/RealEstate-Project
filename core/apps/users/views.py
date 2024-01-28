from rest_framework.decorators import api_view, action
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import filters
from ..pagination import StandardResultsSetPagination
from rest_framework.views import Response

from apps.models import User
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from ..property.serializers import PropertyDetailsSerializers

from . import serializers


class UserProfileViewset(viewsets.ModelViewSet):
    """_summary_

    Args:
        viewsets (_type_): _description_

    Returns:
        _type_: _description_
    """
    serializer_class = serializers.UserProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = '__all__'

    def get_queryset(self):
        return User.objects.filter(is_deleted=False, is_active=True, id=self.request.user.id)


class UpdateUserViewsets(viewsets.ModelViewSet):
    """_summary_

    Args:
        viewsets (_type_): _description_
    """
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UpdateUserSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = '__all__'
    # def update(self, request, *args, **kwargs):
    #     serializer = self.serializer_class(
    #         instance=request.user, data=request.data, partial=True)
    #     if serializer.is_valid(raise_exception=True):
    #         serializer.save()
    #         return Response({
    #             'data': 'User Updated Suscceful',
    #             'user': serializer.data
    #         }, status=200)
    #     else:
    #         return Response({
    #             'error': serializer.errors
    #         }, status=404)

    def partial_update(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            instance=request.user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=200)
        else:
            return Response({
                'error': serializer.errors
            }, status=404)

    def get_queryset(self):

        return User.objects.filter(is_deleted=False, is_active=True)


class UserViewsets(viewsets.ModelViewSet):
    """_summary_

    Args:
        viewsets (_type_): _description_

    Returns:
        _type_: _description_
    """
    serializer_class = serializers. UserSerializer
    permission_classes = []
    filter_backends = [filters.OrderingFilter]
    ordering_fields = '__all__'

    def update(self, request, *args, **kwargs):
        self.serializer_class = serializers.UpdateUserSerializer
        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        return User.objects.filter(is_deleted=False, is_active=True)
