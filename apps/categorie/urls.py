from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.CategoryViewsets.as_view({'get': 'list'})),
]
