from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from rest_framework import serializers

from rest_framework.serializers import (
    HyperlinkedIdentityField,
    ModelSerializer,
    SerializerMethodField,
    ValidationError
    )

from modificationrequests.models import Request, File

User = get_user_model()


class FileSerializer(serializers.ModelSerializer):
    """Serializer for attachted files"""

    class Meta:
        model = File
        fields = '__all__'


def create_request_serializer(model_type='project', slug=None, developer_id=None, user=None):
    class RequestCreateSerializer(ModelSerializer):

        class Meta:
            model = Request
            fields = [
                'id',
                'content',
                'days',
                'budget',
                'timestamp',
            ]

        def __init__(self, *args, **kwargs):
            self.model_type = model_type
            self.slug = slug
            self.user = user
            self.developer_id = developer_id

            return super(RequestCreateSerializer, self).__init__(*args, **kwargs)

        def validate(self, data):
            model_type = self.model_type
            model_qs = ContentType.objects.filter(model=model_type)
            if not model_qs.exists() or model_qs.count() != 1:
                raise ValidationError("This is not a valid content type")
            SomeModel = model_qs.first().model_class()
            obj_qs = SomeModel.objects.filter(slug=self.slug)
            if not obj_qs.exists() or obj_qs.count() != 1:
                raise ValidationError("This is not a slug for this content type")
            return data

        def create(self, validated_data):
            content = validated_data.get("content")
            days = validated_data.get("days")
            budget = validated_data.get("budget")
            if user:
                main_user = user
            else:
                main_user = User.objects.all().first()
            model_type = self.model_type
            developer_id = self.developer_id
            slug = self.slug
            request = Request.objects.create_by_model_type(
                model_type, slug, developer_id, content, days, budget, main_user
            )
            return request

    return RequestCreateSerializer


class RequestSerializer(ModelSerializer):
    """Serializer to view requests"""

    username = serializers.CharField(source='user.username', read_only=True)
    file = FileSerializer(many=True, read_only=True)

    class Meta:
        model = Request
        fields = '__all__'

