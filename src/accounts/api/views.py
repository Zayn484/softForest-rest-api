
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
    #
    # @action(detail=True, methods=["GET"])
    # def recommendations(self, request, id=None):
    #     user = self.get_object()
    #     recommendations = models.Recommendation.objects.filter(user=user)
    #     serializer = serializers.RecommendationSerializer(recommendations, many=True)
    #
    #     return Response(serializer.data, status=200)
    #
    # @action(detail=True, methods=["GET"])
    # def profile(self, request, id=None):
    #     user = self.get_object()
    #     profiles = models.Profile.objects.filter(user=user)
    #     print(profiles)
    #     serializer = serializers.ProfileSerializer(profiles)
    #
    #     return Response(serializer.data, status=200)
    #
    # @action(detail=True, methods="POST")
    # def recommendation(self, request, id=None):
    #     print('Recommendation POST')
    #     user = self.get_object()
    #     data = request.data
    #     data["user"] = user.id
    #     serializer = serializers.RecommendationSerializer(data=data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=201)
    #     return Response(serializer.errors, status=400)
    #
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

    @action(detail=True, methods=["POST"], url_path='upload-profile-picture')
    def upload_profile_picture(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(
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


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserDetailSerializer
    permission_classes = [AllowAny, ]
    queryset = models.User.objects.all()
    lookup_field = 'username'


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
