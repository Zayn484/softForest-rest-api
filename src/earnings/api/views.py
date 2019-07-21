from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import pandas as pd
from earnings.api.serializers import BalanceSerializer, SoldSoftwareSerializer
from earnings.models import Balance, SoldSoftwares
from projects.models import Project
from projects.api.serializers import ProjectCardSerializer

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


class ChartDataAPIView(APIView):
    permission_classes = [AllowAny, ]

    def get(self, request, format=None):
        user = self.request.GET.get("user")
        moncount = tuecount = wedcount = thucount = fricount = satcount = suncount = 0
        s_qs = SoldSoftwares.objects.filter(user=user)
        for s in s_qs:
            day = pd.Timestamp(str(s.timestamp).split()[0]).dayofweek

            if day == 0:
                moncount += 1
            if day == 1:
                tuecount += 1
            if day == 2:
                wedcount += 1
            if day == 3:
                thucount += 1
            if day == 4:
                fricount += 1
            if day == 5:
                satcount += 1
            if day == 6:
                suncount += 1

        labels = ["M", "T", "W", "T", "F", "S", "S"]
        sales = [moncount, tuecount, wedcount, thucount, fricount, satcount, suncount]
        data = {
            'labels': labels,
            'sales': sales
        }
        return Response(data)


class TopSalesViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = ProjectCardSerializer

    def get_queryset(self):
        user = self.request.GET.get('user')
        if user:
            qs = Project.objects.filter(user=user, ratings__gte=4.0).order_by('ratings')[:5]
            return qs
        return Response({
            'status': 'Not found any records'
        })
