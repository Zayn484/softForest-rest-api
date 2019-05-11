from rest_framework import serializers
from projects.models import Project
from carts.models import Cart


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for selected fields of project"""
    class Meta:
        model =  Project
        fields = ['id', 'title', 'image','description','price']


class CartDetailSerializer(serializers.ModelSerializer):
    """Cart Detail Serializer"""
    projects = ProjectSerializer(many=True,read_only=True)

    class Meta:
        model= Cart
        fields = ('id','user','projects','subtotal','total','updated','timestamp')


class CartSerializer(serializers.ModelSerializer):
    """Cart Serializer"""

    class Meta:
        model = Cart
        fields = ('id','user','projects','subtotal','total','updated','timestamp')
        read_only_fields = ('subtotal', 'total')

    def create(self, validated_data):
        user = validated_data['user']
        projects = validated_data['projects']

        instance = Cart.objects.create(user=user)
        instance.projects.add(*projects)
        return instance




