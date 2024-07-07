from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.PropertyViewsets.as_view({'get': 'list'})),
    path('high-rate/',
         views.PropertyViewsets.as_view({'get': 'get_high_rate'})),
    path('bast-seller/', views.BastSellerViewsets.as_view({'get': 'list'})),

    path('by-state/',
         views.PropertyViewsets.as_view({'get': 'get_by_state'})),

    path('create/', views.PropertyCreateAPIView.as_view({'post': 'create'})),
    path('filter/', views.PropertyFilterViewSet.as_view({'post': 'filter'})),
    path('update-list/',
         views.PropertyCreateAPIView.as_view({'post': 'update_list'})),

    path('<int:pk>/', views.PropertyViewsets.as_view({'get': 'retrieve'})),

    path('<int:pk>/update/',
         views.PropertyCreateAPIView.as_view({'put': 'partial_update', 'patch': 'partial_update'})),

    path('<int:pkprop>/reviews/', include('apps.review.urls')),
    path('<int:pk>/by-address/',
         views.PropertyViewsets.as_view({'get': 'get_by_address'})),
]
