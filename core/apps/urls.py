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
    path('review/', include('apps.review.urls')),
    path('ml/', include('apps.ML.urls')),
    path('chat/', include('apps.chat.urls')),
    path('alarms/', include('apps.alarms.urls')),

    # image method
    path('image/<int:pk>/update/', views.ImageViewsets.as_view(
        {'put': 'partial_update', 'patch': 'partial_update'})),
    path('image/feature/create/',
         views.CreatePropertyfeaturedImageViewsets.as_view({'post': 'create'})),
    path('image/property/create/',
         views.CreatePropertyImageViewsets.as_view({'post': 'create'})),
    path('image/<int:pk>/delete/',
         views.ImageViewsets.as_view({'delete': 'destroy'})),

]
