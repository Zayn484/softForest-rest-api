from django.urls import path, include
from .views import (
    InvitationCreateAPIView,
    InvitationViewSet,
    FriendsViewSet,
    MyFriendsViewSet
)
from rest_framework.routers import DefaultRouter

app_name = 'teams'


router = DefaultRouter()
router.register('invitations', InvitationViewSet)
router.register('friends', FriendsViewSet, base_name='friends')
router.register('my-friends', MyFriendsViewSet, base_name='my-friends')

urlpatterns = [
    path('invite/', InvitationCreateAPIView.as_view()),
    path('', include(router.urls))
]
