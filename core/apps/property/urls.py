from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.PropertyViewsets.as_view({'get': 'list'})),
    path('high-rate/',
         views.PropertyViewsets.as_view({'get': 'get_high_rate'})),
    path('bast-seller/', views.BastSellerViewsets.as_view({'get': 'list'})),
    path('create/', views.PropertyCreateAPIView.as_view()),
    path('<int:pk>/', views.PropertyViewsets.as_view({'get': 'retrieve'})),
    path('<int:pkprop>/reviews/', include('apps.review.urls')),
    path('<int:pk>/by-address/',
         views.PropertyViewsets.as_view({'get': 'get_by_address'})),
]
