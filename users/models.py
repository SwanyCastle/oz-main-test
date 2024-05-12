from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

from common.models import Common


class CustomUserManager(BaseUserManager):
    def _create_user(self, email: str, password: str, **extra_fields):
        if not email:
            raise ValueError("이메일은 필수 입력 항목입니다.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str, **extra_fields):
        if extra_fields.get("is_superuser") is True:
            raise ValueError("일반유저를 슈퍼유저로 생성할 수 없습니다")
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin, Common):
    email = models.CharField(max_length=100, unique=True)
    nickname = models.CharField(max_length=255)
    profile_image = models.ImageField(upload_to="profile/", null=True, blank=True)
    is_social = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"

    objects = CustomUserManager()

    def __str__(self) -> str:
        return f"{self.email} / {self.nickname}"
