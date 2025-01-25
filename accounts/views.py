import logging
import os
import re
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.backends import BaseBackend
from django.core.cache import cache
from django.core.signing import BadSignature, Signer
from django.http import HttpResponsePermanentRedirect
from django.utils.encoding import DjangoUnicodeDecodeError, smart_str
from django.utils.http import urlsafe_base64_decode
from django_tenants.utils import schema_context
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from accounts.serializers import (
    AgentSignupSerializer,
    PasswordResetTokenGenerator,
    ResendEmailSerializer,
    ResetPasswordEmailRequestSerializer,
    ResetPasswordSerializer,
    SetNewPasswordSerializer,
    SignupSerializer,
    LoginSerializer,
)
from app.models import AgentProfile, Client, Domain
from services import (
    CustomResponseMixin,
    send_password_reset_email,
    send_signup_verification_email,
)

logger = logging.getLogger(__file__)


class UserSignupView(APIView, CustomResponseMixin):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user_data = serializer.validated_data
            email = user_data["email"]
            try:
                send_signup_verification_email(request, user_data)
                return self.custom_response(
                    status=status.HTTP_201_CREATED,
                    message="Registration initiated. Please check your email to verify your account.",
                )
            except Exception as e:
                return self.custom_response(
                    message=f"Failed to send email: {str(e)}",
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        return self.custom_response(
            status=status.HTTP_400_BAD_REQUEST,
            message="Invalid data provided.",
            data=serializer.errors,
        )


class AgentSignupView(APIView, CustomResponseMixin):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = AgentSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user_data = serializer.validated_data
            email = user_data["email"]
            agency_name = user_data["agency_name"]
            contact_info = user_data["contact_info"]

            cache.set(
                f"user_data_{email}",
                {
                    "email": email,
                    "agency_name": agency_name,
                    "contact_info": contact_info,
                },
                timeout=3600,
            )  # Cache expires in 1 hour
            try:
                send_signup_verification_email(request, user_data)
                return self.custom_response(
                    status=status.HTTP_201_CREATED,
                    message="Registration initiated. Please check your email to verify your account.",
                )
            except Exception as e:
                return self.custom_response(
                    message=f"Failed to send email: {str(e)}",
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        return self.custom_response(
            status=status.HTTP_400_BAD_REQUEST,
            message="Invalid data provided.",
            data=serializer.errors,
        )


class VerifiedUserBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            user = User.objects.get(username=username)
            if user.check_password(password) and user.is_verified:
                return user
        except User.DoesNotExist:
            return None


class ResendEmailView(CustomResponseMixin, APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ResendEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
        else:
            return self.custom_response(
                data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                return self.custom_response(message="Account is already verified.")

            send_signup_verification_email(request, user, "email-verify")
            return self.custom_response(
                status=status.HTTP_201_CREATED,
                message="Registration initiated. Please check your email to verify your account.",
            )

        except User.DoesNotExist:
            return self.custom_response(
                status=status.HTTP_400_BAD_REQUEST,
                message="User with the provided email does not exist.",
            )

        except Exception as ex:
            logger.error(f"{ex}")
            return self.custom_response(
                message=f"Failed to send email: {str(ex)}",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class VerifyCodeView(CustomResponseMixin, APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        code = request.data.get("code")

        if not email or not code:
            return self.custom_response(
                status=status.HTTP_400_BAD_REQUEST,
                message="Email and code are required.",
            )

        cached_code = cache.get(f"auth_code_{email}")
        if not cached_code:
            return self.custom_response(
                status=status.HTTP_400_BAD_REQUEST,
                message="Verification code expired or not found.",
            )

        if str(cached_code) != str(code):
            return self.custom_response(
                status=status.HTTP_400_BAD_REQUEST,
                message="Invalid verification code.",
            )

        user_data = cache.get(f"user_data_{email}")

        if not user_data:
            return self.custom_response(
                status=status.HTTP_400_BAD_REQUEST,
                message="User data is missing or expired.",
            )

        User = get_user_model()
        user = User.objects.filter(email=email).first()

        if not user:
            return self.custom_response(
                status=status.HTTP_404_NOT_FOUND, message="user not found."
            )

        user.is_active = True
        user.save()
        agency_name = user_data.get("agency_name")
        contact_info = user_data.get("contact_info")
        if user.is_agent:
            sanitized_agency_name = re.sub(r"[^a-z0-9-]", "-", agency_name.lower())
            sanitized_agency_name = sanitized_agency_name.strip("-").strip(".")

            domain_name = settings.DOMAIN_NAME
            subdomain = f"{sanitized_agency_name}.{domain_name}"

            if Domain.objects.filter(domain=subdomain).exists():
                return self.custom_response(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=f"The domain '{subdomain}' already exists.",
                )
            trial_duration = getattr(settings, "TRIAL_DURATION_DAYS", 90)
            paid_until = date.today() + timedelta(days=trial_duration)
            try:
                client = Client.objects.create(
                    user=user,
                    name=agency_name,
                    paid_until=paid_until,
                    on_trial=True,
                )
                client.save()

                Domain.objects.create(
                    user=user,
                    domain=subdomain,
                    tenant=client,
                )
                with schema_context(client.schema_name):
                    AgentProfile.objects.create(
                        client=client,
                        user=user,
                        agency_name=agency_name,
                        contact_info=contact_info,
                    )
            except Exception as e:
                user.delete()
                return self.custom_response(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message=f"Error during creation: {str(e)}",
                )
        cache.delete(f"auth_code_{email}")
        cache.delete(f"user_data_{email}")
        return self.custom_response(
            status=status.HTTP_201_CREATED,
            message="Authentication code verified successfully. Your account has been activated.",
        )


class EmailVerifyView(CustomResponseMixin, APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            token = request.query_params.get("token")
            signer = Signer()
            email = signer.unsign(token)

            user = get_user_model().objects.get(email=email)
            if user.is_active:
                return self.custom_response(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="This account is already verified.",
                )

            user.is_active = True
            user.save()
            user_data = cache.get(f"user_data_{email}")

            if not user_data:
                return self.custom_response(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="User data is missing or expired.",
                )
            agency_name = user_data.get("agency_name")
            contact_info = user_data.get("contact_info")

            if user.is_agent:
                sanitized_agency_name = re.sub(r"[^a-z0-9-]", "-", agency_name.lower())
                sanitized_agency_name = sanitized_agency_name.strip("-").strip(".")

                domain_name = settings.DOMAIN_NAME
                subdomain = f"{sanitized_agency_name}.{domain_name}"

                if Domain.objects.filter(domain=subdomain).exists():
                    return self.custom_response(
                        status=status.HTTP_400_BAD_REQUEST,
                        message=f"The domain '{subdomain}' already exists.",
                    )

                trial_duration = getattr(settings, "TRIAL_DURATION_DAYS", 90)
                paid_until = date.today() + timedelta(days=trial_duration)

                try:
                    client = Client.objects.create(
                        user=user,
                        name=agency_name,
                        paid_until=paid_until,
                        on_trial=True,
                    )
                    client.save()

                    Domain.objects.create(
                        user=user,
                        domain=subdomain,
                        tenant=client,
                    )

                    with schema_context(client.schema_name):
                        AgentProfile.objects.create(
                            client=client,
                            user=user,
                            agency_name=agency_name,
                            contact_info=contact_info,
                        )
                except Exception as e:
                    user.delete()  # Rollback user activation if anything goes wrong
                    return self.custom_response(
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        message=f"Error during creation: {str(e)}",
                    )

            # Clean up cached data
            cache.delete(f"user_data_{email}")
        except TypeError as ex:
            logger.error(f"{ex}")
            return self.custom_response(
                status=status.HTTP_400_BAD_REQUEST,
                message="Invalid request, no token provided",
            )
        except BadSignature as ex:
            logger.error(f"{ex}")
            return self.custom_response(
                status=status.HTTP_400_BAD_REQUEST,
                message="Invalid or expired token.",
            )

        except User.DoesNotExist as ex:
            logger.error(f"{ex}")
            return self.custom_response(
                status=status.HTTP_400_BAD_REQUEST, message="User not found."
            )

        return self.custom_response(
            message="Email successfully verified. Your account is now active."
        )


class RequestPasswordEmail(CustomResponseMixin, generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        if User.objects.filter(
            email=email
        ).exists():  # Change this construct to get_or_404
            user = User.objects.get(email=email)

            try:
                send_password_reset_email(request, user)
                return self.custom_response(
                    status=status.HTTP_201_CREATED,
                    message="Registration initiated. Please check your email to verify your account.",
                )
            except Exception as e:
                return self.custom_response(
                    message=f"Failed to send email: {str(e)}",
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return self.custom_response(
            status=status.HTTP_404_NOT_FOUND,
            message="No user found with this email address",
        )


class CustomRedirect(HttpResponsePermanentRedirect):
    permission_classes = [AllowAny]
    allowed_schemes = [os.environ.get("APP_SCHEME"), "http", "https"]


class PasswordTokenCheckAPI(CustomResponseMixin, generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):
        # Use localhost as the default redirect URL during development
        redirect_url = request.GET.get("redirect_url", "http://localhost:3000")

        try:
            # Decode the user ID
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)

            # Validate the token
            if not PasswordResetTokenGenerator().check_token(user, token):
                return CustomRedirect(
                    f"{redirect_url}?token_valid=False&message=Invalid or expired token"
                )

            # If token is valid, redirect with success parameters
            return CustomRedirect(
                f"{redirect_url}?token_valid=True&message=Credentials Valid&uidb64={uidb64}&token={token}"
            )

        except DjangoUnicodeDecodeError:
            # Handle decoding errors gracefully
            return self.custom_response(
                status=status.HTTP_400_BAD_REQUEST,
                message="Invalid UID encoding",
            )

        except User.DoesNotExist:
            # Handle case where user does not exist
            return self.custom_response(
                status=status.HTTP_404_NOT_FOUND, message="User not found"
            )

        except (
            Exception
        ) as e:  # Don't just catch all exceptions in one, handle each case
            return self.custom_response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred",
            )


class SetNewPasswordAPIView(CustomResponseMixin, generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.custom_response(
            data={"success": True, "message": "Password reset success"},
        )


class ValidateOTPAndResetPassword(CustomResponseMixin, generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        # Extract request data
        email = request.data.get("email", "").strip()
        auth_code = request.data.get("auth_code", "")
        new_password = request.data.get("new_password", "").strip()

        # Validate auth_code format
        try:
            auth_code = int(auth_code)
        except ValueError:
            return self.custom_response(
                status=status.HTTP_400_BAD_REQUEST,
                message="Invalid authentication code format. Must be a numeric value.",
            )

        # Check for required fields
        if not email or not auth_code or not new_password:
            return self.custom_response(
                status=status.HTTP_400_BAD_REQUEST,
                message="All fields are required.",
            )

        # Retrieve OTP from cache
        stored_auth_code = cache.get(f"password_reset_code_{email}")

        if stored_auth_code is None:
            return self.custom_response(
                status=status.HTTP_400_BAD_REQUEST,
                message="Authentication code expired or not found.",
            )

        # Convert to integer (safe since it was retrieved as a string)
        try:
            stored_auth_code = int(stored_auth_code)
        except ValueError:
            return self.custom_response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Stored authentication code is corrupted.",
            )

        # Verify OTP
        if stored_auth_code != auth_code:
            return self.custom_response(
                status=status.HTTP_400_BAD_REQUEST, message="Invalid OTP."
            )

        # Verify user existence
        if not User.objects.filter(email=email).exists():
            return self.custom_response(
                status=status.HTTP_404_NOT_FOUND,
                message="User with this email does not exist.",
            )

        # Reset user password
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()

        # Clear the OTP from cache
        cache.delete(f"password_reset_code_{email}")

        return self.custom_response(
            message="Password has been reset successfully.",
        )


class LoginView(CustomResponseMixin, APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)

            return self.custom_response(
                status=status.HTTP_200_OK,
                message="Login successful",
                data={
                    "accessToken": str(refresh.access_token),
                    "refreshToken": str(refresh),
                },
            )

        return self.custom_response(
            status=status.HTTP_400_BAD_REQUEST,
            message="Invalid data provided",
            data=serializer.errors,
        )

