from accounts import models
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from accounts.models import Recommendation, Profile,ForgetPassword


class ProfileImageSerializer(serializers.ModelSerializer):
    """Serializer for user profile image"""

    class Meta:
        model = Profile
        fields = ('id', 'image', )
        read_only_fields = ('id',)


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""

    username = serializers.CharField(source='user.username', required=False)

    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ('id', 'image', )


class RecommendationSerializer(serializers.ModelSerializer):
    """Serializer for user selected recommendations"""

    class Meta:
        model = Recommendation
        fields = ('categories', 'technologies', 'knowledge')


class UserSerializer(serializers.ModelSerializer):
    """Serializer for new profile objects"""

    recommendations = RecommendationSerializer(required=False)
    profile = ProfileSerializer(required=False)

    class Meta:
        model = models.User
        fields = ('id',
                  'email',
                  'username',
                  'password',
                  'occupation',
                  'recommendations',
                  'profile')

        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):

        user = models.User(
            email=validated_data['email'],
            username=validated_data['username'],
            occupation=validated_data['occupation']
        )

        user.set_password(validated_data['password'])
        user.save()

        for key in list(validated_data):
            if key in 'recommendations':
                recommendations = validated_data.pop('recommendations')
                if recommendations:
                    recommendation = models.Recommendation(
                        user=user,
                        categories=recommendations['categories'] or None,
                        technologies=recommendations['technologies'] or None,
                        knowledge=recommendations['knowledge'] or None

                    )
                    recommendation.save()
            if key in 'profile':
                profiles = validated_data.pop('profile')
                if profiles:
                    profile = models.Profile(
                        id=user.id,
                        user=user,
                        profile_name=profiles['profile_name'] or None,
                        profile_title=profiles['profile_title'] or None,
                        overview=profiles['overview'] or None,
                        skills=profiles['skills'] or None
                    )
                    profile.save()

        return user

    def update(self, instance, validated_data):
        user = models.User.objects.get(email=instance.email)
        if validated_data.get('password'):
            user.set_password(validated_data.get('password' or instance.password))
            user.save()
        if validated_data.get('profile'):
            profile = Profile.objects.get(user=instance)
            profile.profile_name = validated_data.get('profile')['profile_name']
            profile.save()
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer for new profile objects"""

    recommendations = RecommendationSerializer(required=False, many=True)
    profile = ProfileSerializer(required=False, many=True)

    class Meta:
        model = models.User
        fields = ('id', 'email', 'username', 'occupation', 'recommendations', 'profile')


class LoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.User
        fields = ('email', 'password')


class TokenSerializer(serializers.ModelSerializer):
    """
    Serializer for Token model.
    """
    class Meta:
        model = Token
        fields = ('key', 'user_id')


class ForgetPasswordSerialier(serializers.ModelSerializer):
    """
        Serializer for Forget Password
    """
    class Meta:
        model = ForgetPassword
        fields = ('user','code')


