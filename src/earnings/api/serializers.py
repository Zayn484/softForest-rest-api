from rest_framework import serializers
from earnings.models import Balance, SoldSoftwares


class BalanceSerializer(serializers.ModelSerializer):
    """Serializer For Balance Model """
    class Meta:
        model = Balance
        fields = '__all__'


class SoldSoftwareSerializer(serializers.ModelSerializer):
    """"Serializer For Sold Projects """
    class Meta:
        model = SoldSoftwares
        fields = '__all__'

