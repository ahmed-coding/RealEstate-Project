from django.urls import path
from . import views
urlpatterns = [
    path('', views.ReviewViewsets.as_view({'get': 'list'})),
    path('create/', views.ReviewViewsets.as_view({'post': 'create'})),
    
]
