from django.urls import path
from . import views

urlpatterns = [
    path('country/', views.CountryViewsets.as_view({'get': 'list'})),
    path('city/', views.CityViewsets.as_view({'get': 'list'})),
    path('state/', views.StateViewsets.as_view({'get': 'list'})),
    path('<int:pk>/update/',
         views.AddressViewsets.as_view({'put': 'partial_update', 'patch': 'partial_update'})),

]
