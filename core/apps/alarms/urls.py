from django.urls import path, include
from . import views
urlpatterns = [
    path('create', views.AlarmViewsets.as_view({'post': 'create'})),

]
