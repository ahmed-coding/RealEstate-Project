from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.BannerViewSetst.as_view({'get': 'list'})),
    path('create/', views.BannerViewSetst.as_view({'post': 'create'}))
]
