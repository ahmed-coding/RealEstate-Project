from django.urls import path, include

urlpatterns = [
    path('auth/', include('apps.authentication.urls')),
    path('categorie/', include('apps.categorie.urls')),
    path('property/', include('apps.property.urls')),
    path('address/', include('apps.address.urls')),
    path('user/', include('apps.users.urls')),
    path('ticket/', include('apps.ticket.urls')),


]
