from rest_framework import serializers
from chat.models import Chat, Contact
from chat.views import get_user_contact


class ContactSerializer(serializers.ModelSerializer):
    """Serializer for contacts"""

    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Contact
        fields = '__all__'

    def to_internal_value(self, data):
        print(data)
        return data


class ChatSerializer(serializers.ModelSerializer):
    """Serializer for chats"""

    participants = ContactSerializer(many=True)

    class Meta:
        model = Chat
        fields = ('id', 'messages', 'participants')

    def create(self, validated_data):
        print(validated_data)
        participants = validated_data.pop('participants')
        chat = Chat()
        chat.save()
        for username in participants:
            contact = get_user_contact(username)
            chat.participants.add(contact)
        chat.save()
        return chat
