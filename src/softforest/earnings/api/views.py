from rest_framework import viewsets
from earnings.api.serializers import BalanceSerializer, SoldSoftwareSerializer
from earnings.models import Balance, SoldSoftwares
from rest_framework.permissions import AllowAny
# Create your views here.


class BalanceViewSet(viewsets.ModelViewSet):
    """ViewSet For Balance Model"""
    serializer_class = BalanceSerializer
    permission_classes = [AllowAny, ]
    lookup_field = 'user'
    model = Balance
    queryset = Balance.objects.all()


class SoldSoftwareViewSet(viewsets.ModelViewSet):
    """Viewset For Sold Softwares Model"""
    serializer_class = SoldSoftwareSerializer
    permission_classes = [AllowAny, ]
    # lookup_field = 'user'
    model = SoldSoftwares

    def get_queryset(self):
        user = self.request.GET.get("user")
        return SoldSoftwares.objects.filter(user=user)
