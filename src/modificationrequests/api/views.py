import os
from django.db.models import Q
from django.contrib.auth import settings
from django.http import HttpResponse
from rest_framework.generics import (
    CreateAPIView,
    )
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.exceptions import NotFound
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from wsgiref.util import FileWrapper
from mimetypes import guess_type

from modificationrequests.models import Request, File
from accounts.models import User

from .serializers import (
    create_request_serializer,
    FileSerializer,
    RequestSerializer
    )


class RequestCreateAPIView(CreateAPIView):
    queryset = Request.objects.all()
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        model_type = self.request.GET.get("type")
        slug = self.request.GET.get("slug")
        user = User.objects.filter(id=self.request.GET.get("user"))
        developer_id = self.request.GET.get("developer_id")
        return create_request_serializer(
                model_type=model_type,
                slug=slug,
                developer_id=developer_id,
                user=user
                )


class FileUploadView(CreateAPIView):
    queryset = File.objects.all()
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        serializer = FileSerializer(
            data=self.request.data
        )

        return FileSerializer


class RequestViewSet(viewsets.ModelViewSet):
    serializer_class = RequestSerializer
    queryset = Request.objects.all()
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Request.objects.all()
        user = self.request.GET.get("user")
        developer = self.request.GET.get("developer")

        if user or developer is not None:
            return Request.objects.filter(
                Q(user=user) |
                Q(developer_id=developer))
        return queryset


class AttachedFileDownloadViewSet(viewsets.ModelViewSet):
    serializer_class = FileSerializer
    queryset = File.objects.all()

    def retrieve(self, request, *args, **kwargs):
        user = self.request.GET.get("user")
        qs = Request.objects.filter(user=user)
        if qs.count() != 1:
            raise NotFound('Not found!!!')
        request_obj = qs.first()
        download_qs = File.objects.filter(request=request_obj)
        if download_qs.count() != 1:
            raise NotFound('Download not found!!!')
        download_obj = download_qs.first()
        file_root = settings.PROTECTED_ROOT
        file_path = download_obj.file.path
        final_filepath = os.path.join(file_root, file_path)  # where the file is stored

        with open(final_filepath, 'rb') as f:
            wrapper = FileWrapper(f)
            mime_type = 'application/force-download'
            guessed_mime_type = guess_type(file_path)[0]  # attached file
            if guessed_mime_type:
                mime_type = guessed_mime_type
            response = HttpResponse(wrapper, content_type=mime_type)
            response['Content-Disposition'] = "attachment;filename=%s" % download_obj.name
            response["X-SendFile"] = str(download_obj.name)
            return response
