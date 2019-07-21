from django.urls import path, include
from .views import (
    ChartDataAPIView,
    TopSalesViewSet
)
from rest_framework.routers import DefaultRouter

app_name = 'earnings'


router = DefaultRouter()
router.register('top-sales', TopSalesViewSet, base_name='top-sales')

urlpatterns = [
    path('daily-sales/', ChartDataAPIView.as_view()),
    path('', include(router.urls))
]
