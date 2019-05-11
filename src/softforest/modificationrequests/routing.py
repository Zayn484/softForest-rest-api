from modificationrequests.consumers import NotifyRequestConsumser
from django.urls import re_path

websocket_urlpatterns = [
    re_path(r'^ws/notifications/$', NotifyRequestConsumser),
]