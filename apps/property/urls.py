from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.PropertyViewsets.as_view({'get': 'list'})),
    path('high-rate/',
         views.PropertyViewsets.as_view({'get': 'get_high_rate'})),
]
