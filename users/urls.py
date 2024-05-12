from django.urls import path

from .views import (  # KakaoSignInView,
    RefreshTokenView,
    SignInView,
    SignOutView,
    SignUpView,
    UserProfileImageView,
    UserDetailView,
)

urlpatterns = [
    path("sign-up", SignUpView.as_view(), name="sign-up"),
    path("sign-in", SignInView.as_view(), name="sign-in"),
    # path('kakao/sign-in', KakaoSignInView.as_view(), name='kakao-sign-in'),
    path("token-refresh", RefreshTokenView.as_view(), name="token-refresh"),
    path("sign-out", SignOutView.as_view(), name="sign-out"),
    path("detail", UserDetailView.as_view(), name="user-detail"),
    path("profile-image", UserProfileImageView.as_view(), name="profile-image"),
]
