# asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from posts import routing  # Importa el enrutamiento de WebSockets

# Establecer el entorno de configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tu_proyecto.settings')

# Crear la aplicación ASGI
application = ProtocolTypeRouter({
    # Manejar las solicitudes HTTP tradicionales con el ASGI de Django
    "http": get_asgi_application(),

    # Manejar WebSockets con el middleware de autenticación
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns  # Usar las rutas de WebSocket definidas en `routing.py`
        )
    ),
})
