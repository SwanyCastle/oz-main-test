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


# def upload_to_s3(file, bucket_name, object_name, content_type):
#     s3_client = boto3.client(
#         "s3", aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
#     )
#     s3_client.upload_fileobj(file, bucket_name, object_name, ExtraArgs={"ContentType": content_type})
#     url = settings.MEDIA_URL + object_name
#     return url
#
#
# class UserProfileImageSerializer(serializers.ModelSerializer[CustomUser]):
#     class Meta:
#         model = CustomUser
#         fields = ("profile_image",)
#
#     @staticmethod
#     def update(instance, validated_data):
#         file = validated_data.get("profile_image", None)
#         if file:
#             file_name = f"profile/user_{instance.id}_{file.name}"
#             content_type = file.content_type
#             url = upload_to_s3(file, settings.AWS_STORAGE_BUCKET_NAME, file_name, content_type)
#             instance.profile_image = url
#         instance.save()
#         return instance
