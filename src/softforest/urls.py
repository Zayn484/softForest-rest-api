from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework import routers
from django.urls import path, include

from accounts.api.views import LoginViewSet, UserViewSet, ProfileViewSet
from projects.api.views import (
    ProjectViewSet,
    ProjectCardViewSet,
    ProjectDetailViewSet,
    FileDownloadViewSet,
    ProjectList,
    ProjectRandomList,
    InfinitView
)

from carts.api.views import CartViewSet, CartDetailView
from orders.api.views import BillingViewSet, OrderViewSet, CardViewSet
from earnings.api.views import BalanceViewSet, SoldSoftwareViewSet

router = routers.DefaultRouter()
router.register('login', LoginViewSet, base_name='login'),
router.register('register', UserViewSet, base_name='register'),
router.register('profiles', ProfileViewSet, base_name='profiles')
router.register('projects', ProjectViewSet, basename='projects'),
router.register('projects-cards', ProjectCardViewSet, basename='projects-cards'),
router.register('projects-detail', ProjectDetailViewSet, base_name='project-detail')
router.register('project-download', FileDownloadViewSet, base_name='project-download')
router.register('cart-details', CartDetailView, base_name='cart-details')
router.register('cart', CartViewSet, base_name='cart')
router.register('billing', BillingViewSet, base_name='billing')
router.register('order', OrderViewSet, base_name='order')
router.register('payment', CardViewSet, base_name='payment')
router.register('balance', BalanceViewSet, base_name='balance')
router.register('sales', SoldSoftwareViewSet, base_name='sales')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/projects-list/<int:id>', ProjectList.as_view()),
    path('api/projects-random-list/', ProjectRandomList.as_view()),
    path('api/infinite-scroll/', InfinitView.as_view()),
    path('api/chat/', include('chat.api.urls', namespace='chat')),
    path('api/comments/', include('comments.api.urls', namespace='comments')),
    path('api/modification-requests/', include('modificationrequests.api.urls', namespace='modificationrequests')),
    path('admin/', admin.site.urls)
]


if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

