from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models


# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, gmail, password=None, **extra_fields):
        if not gmail:
            raise ValueError("the gmail is required")
        gmail = self.normalize_email(gmail)
        user = self.model(gmail=gmail, **extra_fields)

        if password:
            user.set_password(password)
        else:
            raise ValueError("the password is required")
        user.save(using=self._db)
        return user

    def create_staff(self, gmail, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        return self.create_user(gmail, password, **extra_fields)

    def create_superuser(self, gmail, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(gmail, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    user_name = models.CharField(max_length=100, blank=True, null=True)
    gmail = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    user_pic = models.ImageField(upload_to="user_photo/", blank=True, null=True)
    photo_url = models.URLField(blank=True,null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "gmail"
    REQUIRED_FIELDS = ["user_name", "password", "phone_number"]

    def __str__(self):
        return self.gmail
