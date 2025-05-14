from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from django.core.asgi import get_asgi_application
from rest_live.routers import RealtimeRouter

router = RealtimeRouter()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
    URLRouter([
        path("ws/subscribe/", router.as_consumer().as_asgi(), name="subscriptions"),
    ])
),
})