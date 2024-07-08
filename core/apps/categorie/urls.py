from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.CategoryViewsets.as_view({'get': 'list'})),
    path('attributes/',
         views.AttributeByCategorieViewsets.as_view({'get': 'list'})),
    path('features/',
         views.FeatureByCategorieViewsets.as_view({'get': 'list'})),
]
