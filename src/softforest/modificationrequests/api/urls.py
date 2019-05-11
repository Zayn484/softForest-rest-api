from django.urls import path, include, re_path
from .views import (
    RequestCreateAPIView,
    FileUploadView,
    AttachedFileDownloadViewSet,
    RequestViewSet
)
from rest_framework.routers import DefaultRouter

app_name = 'modificationrequests'

router = DefaultRouter()
router.register('', RequestViewSet)
router.register(r'attachment-download', AttachedFileDownloadViewSet)


urlpatterns = [
    path('create/', RequestCreateAPIView.as_view()),
    path('upload-file/', FileUploadView.as_view()),
    path('', include(router.urls))
    #path('notifications/', include(notifications.urls, namespace='notifications')),
]

