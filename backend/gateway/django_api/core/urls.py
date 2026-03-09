"""
Django Gateway URL Configuration
API Gateway URL routing
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/users/', include('gateway.django_api.apps.users.urls')),
    path('api/properties/', include('gateway.django_api.apps.properties.urls')),
    path('api/reviews/', include('gateway.django_api.apps.reviews.urls')),
    path('api/chat/', include('gateway.django_api.apps.chat.urls')),
    path('api/notifications/', include('gateway.django_api.apps.notifications.urls')),

    # Health check
    path('health/', lambda r: __import__('django.http',
         fromlist=['JsonResponse']).JsonResponse({'status': 'ok'})),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
