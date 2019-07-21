from django.db.models import Q
from rest_framework import viewsets, filters
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import action
from accounts import models
from accounts.api import serializers


# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    """Handles creating, reading and updating profiles"""

    serializer_class = serializers.UserSerializer
    queryset = models.User.objects.all()
    permission_classes = [AllowAny, ]
    filter_backends = (filters.SearchFilter, )
    search_fields = ('username', 'email', )
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def get_serializer_class(self):
        if self.action == 'upload_profile_picture':
            return serializers.ProfileImageSerializer
        return self.serializer_class

    @action(detail=True, methods="POST")
    def profile(self, request, id=None):
        user = self.get_object()
        data = request.data
        data["user"] = user.id
        serializer = serializers.ProfileSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ProfileSerializer
    permission_classes = [AllowAny, ]
    queryset = models.Profile.objects.all()
    #lookup_field = 'user'

    def get_queryset(self):
        # For searching profile
        queryset_list = models.Profile.objects.all()
        query = self.request.GET.get("search_profile")
        if query:
            queryset_list = queryset_list.filter(
                Q(profile_name__icontains=query) |
                Q(profile_title__icontains=query)
            ).distinct()

        return queryset_list

    def get_serializer_class(self):
        if self.action == 'upload_profile_picture':
            return serializers.ProfileImageSerializer
        return self.serializer_class

    @action(detail=True, methods=["POST"], url_path='upload-profile-picture')
    def upload_profile_picture(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(
            user,
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data, status=201
            )
        return Response(
            serializer.errors, status=400
        )


class LoginViewSet(viewsets.ViewSet):
    """Checks email and password and return auth token"""

    serializer_class = serializers.LoginSerializer
    permission_classes = [AllowAny, ]

    def create(self, request):
        """Use ObtainAuthToken ApiView to validate and create a token"""
        response = ObtainAuthToken().post(request)
        token = Token.objects.get(key=response.data['token'])
        user_data = models.User.objects.filter(id__iexact=token.user_id).values()
        dict = (user_data[0])
        email = None
        for i in dict:
            if i is 'email':
                email = dict[i]
        user_recommendations = models.Recommendation.objects.filter(user__email__icontains=email).values()
        return Response({'token': token.key,
                         'id': token.user_id,
                         'user_data': user_data,
                         'user_recommendations': user_recommendations})

class ForgetPasswordViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ForgetPasswordSerialier
    lookup_field = 'user'
    def get_queryset(self):
        user = self.request.GET.get('user')
        code = self.request.GET.get('code')
        if user:
            qs = models.ForgetPassword.objects.filter(user=user)
            if qs.exists():
                if qs.first().code == code:
                    return models.ForgetPassword.objects.filter(user=user)
                return models.ForgetPassword.objects.filter(user=None)
        return models.ForgetPassword.objects.all()

