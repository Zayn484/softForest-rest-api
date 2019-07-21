from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path

from chat.consumers import ChatConsumer
from teams.consumers import InvitationConsumer


application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([
            re_path(r'^ws/chat/(?P<room_name>[^/]+)/$', ChatConsumer),
            re_path(r'^ws/invitation/(?P<id>[^/]+)/$', InvitationConsumer)
        ])
    ),
})