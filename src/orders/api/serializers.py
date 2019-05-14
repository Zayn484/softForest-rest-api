from rest_framework import serializers
from orders import models
from projects.models import Project
from projects.api.serializers import FileSerializer


class BillingSerializer(serializers.ModelSerializer):
    """Serializer For Billing Profile"""
    class Meta:
        model = models.Billing
        fields = '__all__'


class CardSerializer(serializers.ModelSerializer):
    """Serializer For Card Model"""
    class Meta:
        model = models.Card
        fields = ('billing_profile','stripe_id','brand','last4')


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for selected fields of project"""
    file = FileSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'title', 'file']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer For Order"""
    project = ProjectSerializer(many=True, read_only=True)

    class Meta:
        model = models.Order
        fields = '__all__'


