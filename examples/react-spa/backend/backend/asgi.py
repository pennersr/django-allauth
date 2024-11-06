"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import logging
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from yourapp import routing  # Import your routing configuration
from channels.security.websocket import AllowedHostsOriginValidator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# Create the ASGI application
application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Handle HTTP requests
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                routing.websocket_urlpatterns  # Your WebSocket URL routing
            )
        )
    ),
})

# Custom error handling (optional)
async def custom_error_middleware(scope, receive, send):
    try:
        await application(scope, receive, send)
    except Exception as e:
        logger.error(f"Error in ASGI application: {e}")
        # Handle the error (send a response, etc.)

# Final application with custom error handling
application = custom_error_middleware(application)