import os

from channels.routing import ProtocolTypeRouter,URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from ChatApp.routing import websocket_urlpatterns
from ChatApp import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back.settings')

# django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket":AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
    # Just HTTP for now. (We can add other protocols later.)
})


