import boto3
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from config.settings import env

from .models import CustomUser
from .serializers import (
    CustomUserSerializer,
    CustomUserUpdateSerializer,
    MyTokenObtainPairSerializer,
    # UserProfileImageSerializer,
)

# import requests


class SignUpView(APIView):
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        user = CustomUser.objects.filter(email=email).exists()
        if user:
            return Response(
                data={
                    "message": "이미 등록된 이메일 입니다.",
                },
                status=status.HTTP_409_CONFLICT,
            )
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {"message": "Successfully Sign Up"}
            return Response(data=response, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignInView(APIView):
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = CustomUser.objects.filter(email=email).first()

        if not user:
            return Response(
                data={
                    "message": "권한이 만료 되었거나 권한이 없습니다.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        pw_chk = user.check_password(password)

        if not pw_chk:
            return Response(
                data={
                    "message": "권한이 만료 되었거나 권한이 없습니다.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = MyTokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.get_token(user)
        refresh_token = str(token)
        access_token = str(token.access_token)
        # serializer = self.serializer_class(user)
        response = Response(
            data={"message": "Successfully Sign In", "access": access_token, "refresh": refresh_token},
            status=status.HTTP_200_OK,
        )

        return response


class SignOutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                data={"status_code": 400, "message": "Refresh Token 정보가 전달되지 않았습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        refresh_token_obj = RefreshToken(refresh_token)
        refresh_token_obj.blacklist()
        response = Response(data={"message": "Successfully Sign Out"}, status=status.HTTP_200_OK)
        return response


# class KakaoSignInView(APIView):
#     permission_classes = [AllowAny]
#
#     def post(self, request, *args, **kwargs):
#         authorization_code = request.data.get('code')
#
#         url = "https://kauth.kakao.com/oauth/token"
#         headers = {"Content-type": "application/x-www-form-urlencoded;charset=utf-8"}
#         data = {
#             "grant_type": "authorization_code",
#             "client_id": env("KAKAO_REST_API_KEY"),
#             "redirect_uri": env("KAKAO_REDIRECT_URI"),
#             "code": authorization_code,
#         }
#         token_response = requests.post(url, headers=headers, data=data)
#         token_response_json = token_response.json()
#         access_token = token_response_json.get('access_token')
#
#         if not access_token:
#             return Response(
#                 data={
#                     "message": "엑세스 토큰이 필요합니다."
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         headers = {"Authorization": f"Bearer {access_token}"}
#         url = "https://kapi.kakao.com/v2/user/me"
#         response = requests.get(url, headers=headers)
#
#         if response.status_code != 200:
#             return Response(
#                 data={
#                     "message": "카카오 계정 정보를 불러오지 못했습니다."
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         user_info = response.json()
#
#         email = user_info.get('kakao_account').get('email')
#         user = CustomUser.objects.filter(email=email).first()
#
#         if not user:
#             user = CustomUser.objects.create(
#                 email=email,
#                 nickname=user_info.get('properties').get('nickname'),
#                 is_social=True
#             )
#             user.set_unusable_password()
#             user.save()
#
#         token = MyTokenObtainPairSerializer.get_token(user)
#         refresh_token = str(token)
#         access_token = str(token.access_token)
#
#         # serializer = CustomUserSerializer(user)
#
#         return Response(
#             data={
#                 "message": "Successfully Sign In",
#                 "access": access_token,
#                 "refresh": refresh_token
#             },
#             status=status.HTTP_200_OK
#         )


class RefreshTokenView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return response


class UserDetailView(APIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get_user(request, user_id):
        try:
            user = CustomUser.objects.filter(pk=user_id).first()
            return user
        except CustomUser.DoesNotExist:
            raise NotFound(detail="해당 유저를 찾을 수 없습니다.")

    def get(self, request):
        user = request.user
        if not user:
            return Response(
                data={
                    "message": "멤버 정보를 찾을 수 없습니다.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = self.serializer_class(user)
        response = {"message": "Successfully Read User Infomation", "user": serializer.data}
        return Response(data=response, status=status.HTTP_200_OK)

    def put(self, request):
        user = request.user
        if not user:
            return Response(
                data={
                    "message": "유저 정보를 찾을 수 없습니다.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = CustomUserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            serializer = self.serializer_class(user)
            response = {"message": "Success", "user": serializer.data}
            return Response(data=response, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        if not user:
            return Response(
                data={
                    "message": "멤버 정보를 찾을 수 없습니다.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.delete()
        return Response(
            data={
                "message": "Successfully Delete User Information",
            },
            status=status.HTTP_200_OK,
        )


# class UploadProfileImageView(APIView):
    # serializer_class = UserProfileImageSerializer
    # permission_classes = [IsAuthenticated]

    # def post(self, request):
    #     user = request.user
    #     db_user = CustomUser.objects.filter(pk=user.id).first()
    #     existing_profile_image = db_user.profile_image
    #     serializer = self.serializer_class(user, data=request.data)
    #
    #     if serializer.is_valid():
    #         if existing_profile_image:
    #             self.delete_s3_file(existing_profile_image)
    #         serializer.save()
    #         return Response(data={"message": "Successfully Upload Profile Image"}, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    # @staticmethod
    # def delete_s3_file(file_url):
    #     s3_client = boto3.client(
    #         "s3", aws_access_key_id=env("AWS_ACCESS_KEY_ID"), aws_secret_access_key=env("AWS_SECRET_ACCESS_KEY")
    #     )
    #
    #     bucket_name = env("AWS_STORAGE_BUCKET_NAME")
    #     prefix = "profile/"
    #     file_name = str(file_url).split("/")[-1]
    #     file_key = prefix + file_name
    #
    #     s3_client.delete_object(Bucket=bucket_name, Key=file_key)
