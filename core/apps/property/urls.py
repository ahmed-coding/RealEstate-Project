from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.PropertyViewsets.as_view({'get': 'list'})),
    path('high-rate/',
         views.PropertyViewsets.as_view({'get': 'get_high_rate'})),
    path('<pk>/', views.PropertyViewsets.as_view({'get': 'retrieve'})),
    path('<prop>/reviews/', include('apps.review.urls')),
    path('<pk>/by-address/',
         views.PropertyViewsets.as_view({'get': 'get_by_address'})),
]
