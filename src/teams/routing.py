from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path, re_path

from .consumers import InvitationConsumer


websocket_urlpatterns = [
    re_path(r'^ws/invitation/(?P<id>[^/]+)/$', InvitationConsumer),
]