from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from carts.api.serializers import CartSerializer, CartDetailSerializer
from carts.models import Cart
# Create your views here.


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    lookup_field = 'user'
    permission_classes = [AllowAny, ]
    model = Cart

    """Get data against user Id"""

    def get_queryset(self,):
        return Cart.objects.all()

    """Partically Update The Objects"""

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class CartDetailView(viewsets.ModelViewSet):
    serializer_class = CartDetailSerializer
    permission_classes = [AllowAny, ]
    lookup_field = 'user'
    model = Cart
    queryset = Cart.objects.all()



