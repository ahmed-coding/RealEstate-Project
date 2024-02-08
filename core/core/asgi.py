import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from dotenv import load_dotenv
from django.urls import path


load_dotenv()


debug = os.environ.get('DEBUG')
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# if debug:
#     os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.local')
# else:
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'core.settings.production')

app = get_asgi_application()
from .urls import websocket_urlpatterns  # noqa isort:skip
from .middleware import TokenAuthMiddleware  # noqa isort:skip
from apps.chat.consumers import ChatConsumer  # noqa isort:skip
from apps.notifications.consumers import NotificationConsumer  # noqa isort:skip

application = ProtocolTypeRouter(
    {
        "http": app,
        "websocket": TokenAuthMiddleware(
            AllowedHostsOriginValidator(
                AuthMiddlewareStack(
                    URLRouter([
                        # websocket_urlpatterns
                        path("ws/notifications/", NotificationConsumer.as_asgi()),
                        path('ws/chat/<room_id>/', ChatConsumer.as_asgi()),
                    ])
                )
            )
        ),
    }
)
