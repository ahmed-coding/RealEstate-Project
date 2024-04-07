from django.urls import path, include
from . import views

urlpatterns = [
    # path('state/', views..as_view({'get', 'list'}))
    path("profile/",
         views.UserProfileViewset.as_view({'get': 'list'}), name="profile"),
    path("profile/<int:pk>/",
         views.UserProfileViewset.as_view({'get': 'retrieve'}), name="user_profile"),
    path('profile/update/',
         views.UpdateUserViewsets.as_view({'put': 'partial_update', 'patch': 'partial_update'})),
    path('favorite/', include('apps.favorite.urls')),


]
