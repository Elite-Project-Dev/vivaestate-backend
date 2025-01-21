import re

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from accounts.models import User
from app.models import AgentProfile


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ["email", "username", "password", "first_name", "last_name"]

    def validate(self, attrs):
        username = attrs.get("username")
        email = attrs.get("email")
        existing_user = User.objects.filter(username=username).first()

        if existing_user:
            if not existing_user.is_active:
                existing_user.delete()
            else:
                raise serializers.ValidationError(
                    "A user with this username already exists and is active."
                )
        existing_user_by_email = User.objects.filter(email=email).first()
        if existing_user_by_email and not existing_user_by_email.is_active:
            existing_user_by_email.delete()
        elif existing_user_by_email:
            raise serializers.ValidationError(
                "A user with this email already exists and is active."
            )

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        return user


class AgentSignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    agency_name = serializers.CharField(required=True, max_length=255)
    contact_info = serializers.CharField()

    class Meta:
        model = AgentProfile  # Link to the actual model that this serializer represents
        fields = [
            "email",
            "username",
            "password",
            "first_name",
            "last_name",
            "agency_name",
            "contact_info",
        ]

    def validate(self, attrs):
        username = attrs.get("username")
        email = attrs.get("email")
        existing_user = User.objects.filter(username=username).first()

        if existing_user:
            if not existing_user.is_active:
                existing_user.delete()
            else:
                raise serializers.ValidationError(
                    "A user with this username already exists and is active."
                )
        existing_user_by_email = User.objects.filter(email=email).first()
        if existing_user_by_email and not existing_user_by_email.is_active:
            existing_user_by_email.delete()
        elif existing_user_by_email:
            raise serializers.ValidationError(
                "A user with this email already exists and is active."
            )

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            is_active=False,
            is_agent=True,
        )
        return user


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    redirect_url = serializers.CharField(max_length=500, required=False, read_only=True)

    class Meta:
        fields = ["email"]


class ResendEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = [
            "password",
            "token",
            "uidb64",
        ]

    def validate(self, attrs):
        try:
            password = attrs.get("password")
            token = attrs.get("token")
            uidb64 = attrs.get("uidb64")

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("The reset link is invalid", 401)

            user.set_password(password)
            user.save()

            return user
        except Exception as e:
            raise AuthenticationFailed("The reset link is invalid", 401)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    auth_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8)

    class Meta:
        model = User
        fields = ["email", "auth_code", "new_password"]
