from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer

from users.models import CustomUser


class UserSignUpSerializer(UserCreateSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class UserGetSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')          
        if request.user.is_authenticated:
            return request.user.follower.filter(
                author=obj
            ).exists()
        return False
