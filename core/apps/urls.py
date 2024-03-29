from django.urls import path, include
from . import views
urlpatterns = [
    path('auth/', include('apps.authentication.urls')),
    path('categorie/', include('apps.categorie.urls')),
    path('property/', include('apps.property.urls')),
    path('address/', include('apps.address.urls')),
    path('user/', include('apps.users.urls')),
    path("friends/", include('apps.friend.urls')),
    path('ticket/', include('apps.ticket.urls')),
    path('friend/', include('apps.friend.urls')),
    path('banners/', include('apps.banners.urls')),

    # image method
    path('image/<int:pk>/update/', views.ImageViewsets.as_view(
        {'put': 'partial_update', 'patch': 'partial_update'})),
    path('image/<int:pk>/delete/',
         views.ImageViewsets.as_view({'delete': 'destroy'})),

]
