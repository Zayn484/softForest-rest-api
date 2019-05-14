from django.urls import path,re_path
from .views import (
    CommentCreateAPIView,
    CommentListAPIView,
    CommentDetailAPIView,
)

app_name = 'comments'

urlpatterns = [
    path('', CommentListAPIView.as_view()),
    path('create/', CommentCreateAPIView.as_view()),
    re_path(r'^(?P<pk>\d+)/$', CommentDetailAPIView.as_view())
]