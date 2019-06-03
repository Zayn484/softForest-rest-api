from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    DestroyAPIView
)
from chat.models import Chat, Contact
from chat.views import get_user_contact
from .serializers import ChatSerializer

User = get_user_model()


class ChatListView(ListAPIView):
    serializer_class = ChatSerializer
    permission_classes = (permissions.AllowAny, )

    def get_queryset(self):
        queryset = Chat.objects.all()
        username = self.request.query_params.get('username', None)
        group = self.request.GET.get('group')
        if username is not None:
            contact = get_user_contact(username)
            queryset = contact.chats.filter(group=False)
        if username and group:
            contact = get_user_contact(username)
            queryset = contact.chats.filter(group=True)

        return queryset


class ChatDetailView(RetrieveAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = (permissions.AllowAny, )


class ChatCreateView(CreateAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = (permissions.AllowAny, )


# class ChatUpdateView(UpdateAPIView):
#     queryset = Chat.objects.all()
#     serializer_class = ChatSerializer
#     permission_classes = (permissions.IsAuthenticated, )
#

class ChatDeleteView(DestroyAPIView):
    serializer_class = ChatSerializer
    permission_classes = (permissions.AllowAny, )

    def delete(self, request, *args, **kwargs):
        if request.GET.get("id"):
            Chat.objects.get(id=request.GET.get("id")).delete()
            return Response({
                'status': 'deleted'
            })


