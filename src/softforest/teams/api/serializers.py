from rest_framework import serializers
from teams.models import Invitation,Friend
from collections import ChainMap
from accounts.models import Profile

class InvitationSerializer(serializers.ModelSerializer):

    profile = serializers.SerializerMethodField()
    accepted = serializers.BooleanField(required=False)

    class Meta:
        model = Invitation
        fields = '__all__'

    def create(self, validated_data):
        user = validated_data['user']
        recipient = validated_data['recipient']
        instance = Invitation.objects.create(user=user, recipient=recipient)
        return instance

    def get_profile(self, obj):
        user = obj
        obj = Profile.objects.get(user__username=user)
        qs = Profile.objects.filter(user__email=obj).values()
        data = dict(ChainMap(*qs))
        return data

class ProfileSerializer(serializers.ModelSerializer):
    """Profile Serializer"""
    class Meta:
        model = Profile
        fields = ('user','profile_name','image','profile_title')
        extra_kwargs = {
            'image': {'read_only': True},
            'profile_name': {'read_only': True},
            'profile_title': {'read_only': True},
        }
        

class FriendsSerializer(serializers.ModelSerializer):
    """Serializer For Team Mambers"""
    #members = ProfileSerializer(many=True)
    
    class Meta:
        model = Friend
        fields = '__all__'
    # def create(self, validated_data):
    #     print(validated_data)
    #     user = validated_data['user']
    #     members = validated_data['members']
    #
    #     instance = Friend.objects.create(user=user)
    #     instance.members.add(*members)
    #     return instance

class MyFriendSerializer(serializers.ModelSerializer):
    members = ProfileSerializer(many=True)
    class Meta:
        model = Friend
        fields='__all__'
    



