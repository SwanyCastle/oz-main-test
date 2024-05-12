from django.conf import settings
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser
import boto3


class CustomUserSerializer(serializers.ModelSerializer[CustomUser]):
    class Meta:
        model = CustomUser
        fields = ("id", "email", "password", "nickname", "profile_image", "created_at", "updated_at")
        extra_kwargs = {"password": {"write_only": True}}

    @staticmethod
    def create(validated_data):
        if validated_data.get("nickname") is not None:
            user = CustomUser.objects.create_user(
                email=validated_data["email"], password=validated_data["password"], nickname=validated_data["nickname"]
            )
            return user
        user = CustomUser.objects.create_superuser(email=validated_data["email"], password=validated_data["password"])
        return user


class CustomUserUpdateSerializer(serializers.ModelSerializer[CustomUser]):
    nickname = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = ("id", "email", "password", "nickname", "profile_image", "created_at", "updated_at")

    @staticmethod
    def update(instance, validated_data):
        if validated_data.get("nickname", "") != "":
            instance.nickname = validated_data.get("nickname")

        if validated_data.get("password", "") != "":
            password = validated_data["password"]
            instance.password = make_password(password)

        instance.save()
        return instance


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["id"] = user.id
        token["email"] = user.email
        token["name"] = user.nickname

        return token


class UserProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['profile_image']
