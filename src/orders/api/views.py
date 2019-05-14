from rest_framework import viewsets
from orders.api import serializers
from orders.models import Billing, Order, Card
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
# import stripe
# STRIPE_SECRET_KEY = getattr(settings,'STRIPE_SECRET_KEY','')
# STRIPE_PUB_KEY = getattr(settings,'STRIPE_PUB_KEY','')
# stripe.api_key=STRIPE_SECRET_KEY
# Create your views here.


class BillingViewSet(viewsets.ModelViewSet):
    """ViewSet For Billing Profile"""

    serializer_class = serializers.BillingSerializer
    permission_classes = [AllowAny, ]
    lookup_field = 'user'
    model = Billing

    def get_queryset(self):
        return Billing.objects.all()


class CardViewSet(viewsets.ModelViewSet):
    """ViewSet For Card """

    serializer_class = serializers.CardSerializer
    permission_classes = [AllowAny, ]
    model = Card
    lookup_field = 'billing_profile'
    queryset = Card.objects.all()


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet For Order"""

    serializer_class = serializers.OrderSerializer
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]
    model = Order

    def get_queryset(self):
        user = self.request.GET.get("user")
        return Order.objects.filter(user=user)

