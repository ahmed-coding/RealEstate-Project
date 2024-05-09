from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

# from apps.cart.serializers import CreateFavoriteSerializers
from ..pagination import StandardResultsSetPagination
from rest_framework.views import Response

from apps.models import Favorite,  Review
from . import serializers

# Create your views here.


class FavoriteView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['prop', ]
    filterset_fields = ['prop',]
    ordering_fields = '__all__'
    # serializer_class = serializers.FavoriteSerializers
    lookup_field = 'prop_id'

    def get_serializer_context(self):
        return {'user': self.request.user}

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CreateFavoriteSerializers
        else:
            return serializers.FavoriteSerializers

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer_class()
        ser = serializers.CreateFavoriteSerializers(
            data=request.data, context={'user': request.user})
        # print(
        # f"User: {request.user}, Product ID: {request.data.get('product')}")

        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(status.HTTP_200_OK)

    def get_queryset(self):
        return Favorite.objects.filter(user__id=self.request.user.id).select_related('user', 'prop')

    @action(detail=True)
    def destroy_list(self, request, *args, **kwargs):
        """Delete List of Favorite

        Args:
            `id`: id of favorite `(NOT PROPERTY)`
            ex:
            ```
            [
                {
                    "id":1
                },
                {
                    "id":2
                },
                {
                    "id":3
                }
            ]
            ```
        Returns:
            data-done: if is ok
        """
        item = self.request.data
        # print(item)
        querysets = self.get_queryset()
        if item:
            try:
                for id in item:
                    querysets.filter(
                        user_id=self.request.user.id, id=id.get('id')).delete()
                return Response({
                    'data': 'Done'
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'error': f'error {e}'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_200_OK)
