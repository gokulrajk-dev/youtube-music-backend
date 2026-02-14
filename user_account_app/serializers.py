from rest_framework import serializers

from .models import *


class customusserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["user_name", "gmail", "password", "phone_number", "photo_url"]
        extra_kwergs = {"password": {"write_only": True}}

        def create(self, validate_data):
            password = validate_data.pop("password")
            user = CustomUser(**validate_data)
            user.set_password(password)
            user.save()
            return user


class get_all_user(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields=['gmail','user_name','phone_number','photo_url','password']