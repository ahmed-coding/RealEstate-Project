from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.BannerViewSetst.as_view({'get': 'list'})),
]
