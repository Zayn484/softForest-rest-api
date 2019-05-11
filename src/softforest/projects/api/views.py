from django.db.models import Q
from django.http import HttpResponse
from rest_framework import viewsets, generics
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from django_filters import rest_framework as filters
from rest_framework.decorators import action
from wsgiref.util import FileWrapper
from mimetypes import guess_type
from operator import or_
from functools import reduce
from rest_framework.permissions import (
    AllowAny,
)
from projects.api.serializers import (
    ProjectSerializer,
    ProjectCardSerializer,
    ProjectDetailSerializer,
    ModuleSerializer,
    TechnologySerializer,
    RequirementSerializer,
    SnapshotSerializer,
    ThumbnailSerializer,
    VideoSerializer,
    FileSerializer
)
from projects.models import *

# Create your views here.


def inifinte_filter(request):
    limit = request.GET.get("limit")
    offset = request.GET.get("offset")
    return Project.objects.all()[int(offset): int(offset) + int(limit)]


def has_more_data(request):
    offset = request.GET.get("offset")
    if int(offset) > Project.objects.all().count():
        return False
    return True


class ProjectList(generics.ListAPIView):
    serializer_class = ProjectDetailSerializer
    permission_classes = [AllowAny, ]

    def get_queryset(self):
        id = self.kwargs['id']
        return Project.objects.filter(user=id)


class ProjectRandomList(generics.ListAPIView):
    serializer_class = ProjectCardSerializer
    permission_classes = [AllowAny, ]

    def get_queryset(self):
        queryset_list = Project.objects.filter(id__gte=0)
        query = self.request.GET.get("q")
        id = self.request.GET.get("id")
        if query:
            queryset_list = queryset_list.filter(
                Q(category__iexact=query) &
                ~Q(id=id) &
                Q(ratings__gte=4.0)
            ).random(8)
        return queryset_list


class ProjectViewSet(viewsets.ModelViewSet):
    """A viewset for viewing and manipulating user instances"""

    serializer_class = ProjectSerializer
    # lookup_field = 'id'
    permission_classes = [AllowAny, ]
    filter_backends = (filters.DjangoFilterBackend, )
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def get_queryset(self):
        # For searching and filtering

        queryset_list = Project.objects.all().order_by('-timestamp')
        query = self.request.GET.get("q")
        categories = self.request.GET.get("categories")
        technologies = self.request.GET.get("technologies")
        prices = self.request.GET.get("price")

        category_params = []
        technology_params = []
        price_params = []

        if technologies is not None:
            for technology in technologies.split('|'):
                technology_params.append(str(technology))

        if categories is not None:
            for category in categories.split('|'):
                category_params.append(str(category))

        if prices is not None:
            for price in prices.split('|'):
                price_params.append(str(price))

        if categories is not None:
            queryset_list = queryset_list.filter(reduce(or_, [Q(category__icontains=t) for t in category_params]))

        if technologies is not None:
            queryset_list = queryset_list.filter(reduce(or_, [Q(technologies__name__icontains=t) for t in technology_params]))

        if prices is not None:
            if 'Free' in price_params:
                queryset_list = queryset_list.filter(price=0)
            if 'Paid' in price_params:
                queryset_list = queryset_list.filter(price__gt=0)

        if query:
            queryset_list = queryset_list.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            ).distinct()

        return queryset_list

    def get_serializer_class(self):
        if self.action == 'upload_thumbnail':
            return ThumbnailSerializer
        if self.action == 'upload_snapshot':
            return SnapshotSerializer
        if self.action == 'upload_video':
            return VideoSerializer
        if self.action == 'upload_file':
            return FileSerializer
        return self.serializer_class

    @action(detail=True, methods=["GET"])
    def modules(self, request, id=None):
        project = self.get_object()
        modules = Module.objects.filter(project=project)
        serializer = ModuleSerializer(modules, many=True)

        return Response(serializer.data, status=200)

    @action(detail=True, methods=["GET"])
    def technologies(self, request, id=None):
        project = self.get_object()
        technologies = Technology.objects.filter(project=project)
        serializer = TechnologySerializer(technologies, many=True)

        return Response(serializer.data, status=200)

    @action(detail=True, methods=["GET"])
    def requirements(self, request, id=None):
        project = self.get_object()
        requirements = Requirement.objects.filter(project=project)
        serializer = RequirementSerializer(requirements, many=True)

        return Response(serializer.data, status=200)

    @action(detail=True, methods=['POST'])
    def project(self, request, id=None):
        project = self.get_object()
        data = request.data
        data["project"] = project.id
        serializer = ProjectSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['POST'], url_path='upload-thumbnail')
    def upload_thumbnail(self, request, pk=None):
        project = self.get_object()
        serializer = self.get_serializer(
            project,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data, status=201
            )

        return Response(
            serializer.errors,
            status=400
        )

    @action(detail=True, methods=['POST'], url_path='upload-snapshot')
    def upload_snapshot(self, request, pk=None):
        project = self.get_object()
        serializer = self.get_serializer(
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data, status=201
            )

        return Response(
            serializer.errors,
            status=400
        )

    @action(detail=True, methods=['POST'], url_path='upload-video')
    def upload_video(self, request, pk=None):
        project = self.get_object()
        serializer = self.get_serializer(
            project,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data, status=201
            )

        return Response(
            serializer.errors,
            status=400
        )

    @action(detail=True, methods=['POST'], url_path='upload-file')
    def upload_file(self, request, pk=None):
        project = self.get_object()
        serializer = self.get_serializer(
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data, status=201
            )

        return Response(
            serializer.errors,
            status=400
        )


class ProjectCardViewSet(viewsets.ModelViewSet):
    """ Viewset for viewing project cards"""

    serializer_class = ProjectCardSerializer
    queryset = Project.objects.all()
    lookup_field = 'slug'
    permission_classes = [AllowAny, ]
    filter_backends = (filters.DjangoFilterBackend,)
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query in ['desktop', 'mobile', 'web']:
            # query to list projects based on category
            queryset = Project.objects.filter(category=query.capitalize()).order_by('-timestamp')[:15]
        elif query == "top-projects":
            # query to return top rated projects
            queryset = Project.objects.filter(ratings__gte=4.0).order_by('-timestamp')[:15]
        else:
            # query to return all projects
            queryset = Project.objects.all().order_by('-timestamp')[:15]
        return queryset


class ProjectDetailViewSet(viewsets.ModelViewSet):
    """A viewset for viewing and manipulating user instances"""

    serializer_class = ProjectDetailSerializer
    queryset = Project.objects.all()
    lookup_field = 'slug'
    permission_classes = [AllowAny, ]
    filter_backends = (filters.DjangoFilterBackend,)
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def get_serializer_class(self):
        if self.action == 'upload_snapshot':
            print('UPLOAD_SNAPSHOT')
            return SnapshotSerializer
        return self.serializer_class

    @action(detail=True, methods=["GET"])
    def modules(self, request, id=None):
        project = self.get_object()
        modules = Module.objects.filter(project=project)
        serializer = ModuleSerializer(modules, many=True)

        return Response(serializer.data, status=200)

    @action(detail=True, methods=["GET"])
    def technologies(self, request, id=None):
        project = self.get_object()
        technologies = Technology.objects.filter(project=project)
        serializer = TechnologySerializer(technologies, many=True)

        return Response(serializer.data, status=200)

    @action(detail=True, methods=["GET"])
    def requirements(self, request, id=None):
        project = self.get_object()
        requirements = Requirement.objects.filter(project=project)
        serializer = RequirementSerializer(requirements, many=True)

        return Response(serializer.data, status=200)


class FileDownloadViewSet(viewsets.ModelViewSet):
    serializer_class = FileSerializer
    queryset = ProjectFile.objects.all()
    permission_classes = [AllowAny, ]

    def retrieve(self, request, *args, **kwargs):
        slug = self.request.GET.get("slug")
        pk = self.request.GET.get("pk")
        qs = Project.objects.filter(slug=slug)
        if qs.count() != 1:
            raise NotFound('Not found!!!')
        project_obj = qs.first()
        download_qs = ProjectFile.objects.filter(project=project_obj)
        if download_qs.count() != 1:
            raise NotFound('Download not found!!!')
        download_obj = download_qs.first()
        file_root = settings.PROTECTED_ROOT
        file_path = download_obj.file.path
        final_filepath = os.path.join(file_root, file_path)  # where the file is stored

        with open(final_filepath, 'rb') as f:
            wrapper = FileWrapper(f)
            mime_type = 'application/force-download'
            guessed_mime_type = guess_type(file_path)[0]  # file.zip
            if guessed_mime_type:
                mime_type = guessed_mime_type
            response = HttpResponse(wrapper, content_type='text/plain')
            response['Content-Disposition'] = "attachment;filename=%s" % download_obj.name
            response["X-SendFile"] = str(download_obj.name)
            return response


class InfinitView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny, ]

    def get_queryset(self):
        qs = inifinte_filter(self.request)
        return qs

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({
            "projects": serializer.data,
            "has_more": has_more_data(request)
        })


