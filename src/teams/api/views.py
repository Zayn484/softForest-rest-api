from django.db.models import Q
from rest_framework.generics import CreateAPIView
from rest_framework.viewsets import ModelViewSet
from teams.models import Invitation,Friend
from .serializers import InvitationSerializer,FriendsSerializer,MyFriendSerializer


class InvitationCreateAPIView(CreateAPIView):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer


class InvitationViewSet(ModelViewSet):
    serializer_class = InvitationSerializer
    queryset = Invitation.objects.all()
    lookup_field = 'user'

    def get_queryset(self):
        queryset = Invitation.objects.all()
        user = self.request.GET.get("user")
        recipient = self.request.GET.get("recipient")
        accepted = self.request.GET.get("accepted")

        if (user or recipient) and accepted is not None:
            return Invitation.objects.filter(
                (Q(user=user) |
                Q(recipient=recipient)) &
                Q(accepted=accepted)
            ).order_by('-timestamp')

        if user or recipient is not None:
            return Invitation.objects.filter(
                Q(user=user) |
                Q(recipient=recipient) &
                Q(accepted=False)).order_by('-timestamp')

        return queryset


class FriendsViewSet(ModelViewSet):
    """ViewSet For TeamMembers Model"""

    serializer_class = FriendsSerializer
    lookup_field = 'user'
    queryset = Friend.objects.all()


class MyFriendsViewSet(ModelViewSet):
    serializer_class = MyFriendSerializer
    lookup_field = 'user'
    queryset = Friend.objects.all()