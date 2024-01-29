import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from dotenv import load_dotenv

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


application = ProtocolTypeRouter(
    {
        "http": app,
        "websocket": TokenAuthMiddleware(
            AllowedHostsOriginValidator(
                AuthMiddlewareStack(
                    URLRouter(
                        websocket_urlpatterns
                    )
                )
            )
        ),
    }
)
