import re

import phonenumbers
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db.models import Q
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from apps.accounts.models import User


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    whatsapp_number = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "password",
            "first_name",
            "last_name",
            "whatsapp_number",
        ]

    def validate(self, attrs):
        username = attrs.get("username")
        email = attrs.get("email")
        whatsapp_number = attrs.get("whatsapp_number")
        existing_user = User.objects.filter(
            Q(username=username) | Q(email=email)
        ).first()

        if existing_user:
            if existing_user.is_active:
                raise serializers.ValidationError(
                    "A user with this email or username already exists and is active."
                )
            existing_user.delete()
        try:
            parsed_number = phonenumbers.parse(
                whatsapp_number, None
            )  # Auto-detect country
            if not phonenumbers.is_valid_number(parsed_number):
                raise serializers.ValidationError(
                    {"whatsapp_number": "Invalid phone number."}
                )
        except phonenumbers.NumberParseException:
            raise serializers.ValidationError(
                {"whatsapp_number": "Invalid phone number format."}
            )

        return attrs


class AgentSignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    agency_name = serializers.CharField(required=True, max_length=255)
    whatsapp_number = serializers.CharField(required=True)

    class Meta:
        model = User  # Link to the actual model that this serializer represents
        fields = [
            "email",
            "username",
            "password",
            "first_name",
            "last_name",
            "agency_name",
            "whatsapp_number",
        ]

    def validate(self, attrs):
        username = attrs.get("username")
        email = attrs.get("email")
        whatsapp_number = attrs.get("whatsapp_number")

        existing_user = User.objects.filter(
            Q(username=username) | Q(email=email)
        ).first()

        if existing_user:
            if existing_user.is_active:
                raise serializers.ValidationError(
                    "A user with this email or username already exists and is active."
                )
            existing_user.delete()  # Only delete inactive users
        try:
            parsed_number = phonenumbers.parse(
                whatsapp_number, None
            )  # Auto-detect country
            if not phonenumbers.is_valid_number(parsed_number):
                raise serializers.ValidationError(
                    {"whatsapp_number": "Invalid phone number."}
                )
        except phonenumbers.NumberParseException:
            raise serializers.ValidationError(
                {"whatsapp_number": "Invalid phone number format."}
            )

        return attrs


class CompleteSignUp(serializers.Serializer):
    agent = serializers.BooleanField(source="is_agent", required=True)
    whatsapp_number = serializers.CharField(required=True)

    def validate(self, attrs):
        whatsapp_number = attrs.get("whatsapp_number")
        try:
            parsed_number = phonenumbers.parse(whatsapp_number, None)
            if not phonenumbers.is_valid_number(parsed_number):
                raise serializers.ValidationError(
                    {"whatsapp_number": "Invalid phone number"}
                )
        except phonenumbers.NumberParseException:
            raise serializers.ValidationError(
                {"whatsapp_number": "Invalid phone number format."}
            )
        return attrs


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    redirect_url = serializers.CharField(max_length=500, required=False, read_only=True)

    class Meta:
        fields = ["email"]


class ResendEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)


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


class LoginSerializer(serializers.Serializer):
    email_or_username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email_or_username = data.get("email_or_username")
        password = data.get("password")
        try:
            if "@" in email_or_username:
                user = User.objects.get(email=email_or_username)
            else:
                user = User.objects.get(username=email_or_username)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email/username or password.")
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email, or password.")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")
        return user
