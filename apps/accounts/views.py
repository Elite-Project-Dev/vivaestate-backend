import logging
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.core.cache import cache
from django.core.signing import BadSignature, Signer
from django.http import HttpResponsePermanentRedirect
from django.utils.encoding import DjangoUnicodeDecodeError, smart_str
from django.utils.http import urlsafe_base64_decode
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from drf_yasg import openapi
from rest_framework import generics, parsers, status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import AgentProfile, User
from apps.accounts.serializers import (
    AgentSignupSerializer,
    LoginSerializer,
    PasswordResetTokenGenerator,
    ResendEmailSerializer,
    ResetPasswordEmailRequestSerializer,
    ResetPasswordSerializer,
    SetNewPasswordSerializer,
    SignupSerializer,
    VerifyCodeSerializer,
)
from services import (
    CreateResponseSerializer,
    CustomResponseMixin,
    EmailService,
    ErrorDataResponseSerializer,
    ErrorResponseSerializer,
    NotFoundResponseSerializer,
    SuccessResponseSerializer,
)

logger = logging.getLogger(__file__)

tags = ["auth"]


class UserSignupView(APIView, CustomResponseMixin):
    """
    API endpoint for user registration.

    Allows new users to sign up by providing necessary details.
    Sends a verification email after successful registration.
    """

    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="User Signup",
        description="Register a new user and send a verification email.",
        tags=tags,
        responses={
            201: CreateResponseSerializer,
            400: ErrorDataResponseSerializer,
            500: ErrorResponseSerializer,
        },
        auth=[],
    )
    def post(self, request, *args, **kwargs):
        """Handle user registration."""
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user_data = serializer.validated_data
            email = user_data["email"]
            cache.set(
                f"user_data_{email}",
                user_data,
                timeout=3600,
            )  # Cache expires in 1 hour
            try:
                email_service = EmailService()
                email_service.send_signup_verification_email(request, user_data)
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
    """
    API endpoint for agent registration.

    Allows real estate agents to sign up by providing necessary details.
    Stores user data in cache temporarily and sends a verification email.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        description="Register a new agent and send a verification email.",
        request=AgentSignupSerializer,
        responses={
            201: CreateResponseSerializer,
            400: ErrorDataResponseSerializer,
            500: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                "Example Request",
                summary="Example agent signup payload",
                description="A sample request payload for agent signup.",
                value={
                    "email": "agent@example.com",
                    "username": "agent123",
                    "password": "securepassword",
                    "first_name": "John",
                    "last_name": "Doe",
                    "agency_name": "Doe Realty",
                    "whatsapp_number": "+2348123456789",
                },
                request_only=True,
            )
        ],
    )
    def post(self, request, *args, **kwargs):
        """Handles agent registration."""
        serializer = AgentSignupSerializer(data=request.data)
        if serializer.is_valid():
            user_data = serializer.validated_data
            user_data["is_agent"] = True
            email = user_data["email"]
            cache.set(
                f"user_data_{email}",
                user_data,
                timeout=3600,
            )  # Cache expires in 1 hour
            try:
                email_service = EmailService()
                email_service.send_signup_verification_email(request, user_data)
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
    """
    API endpoint to resend email verification.

    This view allows users to request a new verification email
    if they haven't received one or their previous link expired.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        description="Resend email verification to the user if not yet verified.",
        request=ResendEmailSerializer,
        responses={
            201: CreateResponseSerializer,
            200: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
            500: ErrorResponseSerializer,
        },
    )
    def post(self, request, *args, **kwargs):
        """Handles email verification resending."""
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
            email_service = EmailService()
            email_service.send_signup_verification_email(request, user)
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
    """
    API endpoint for verifying authentication codes.

    This view verifies the OTP sent to the user’s email and activates their account upon successful validation.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        request=VerifyCodeSerializer,  # Defines expected request body
        responses={
            200: OpenApiResponse(
                description="Authentication code verified successfully. Your account has been activated."
            ),
            400: OpenApiResponse(
                description="Invalid data provided (e.g., missing email/code, expired code)."
            ),
            404: OpenApiResponse(description="User not found."),
            500: OpenApiResponse(description="Server error during verification."),
        },
    )
    def post(self, request, *args, **kwargs):
        """Handles authentication code verification.

        **Request Body:**
        - `email` (string, required) → User's registered email address.
        - `code` (string, required) → 6-digit verification code."""
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

        try:
            user = User.objects.create_user(
                email=user_data["email"],
                username=user_data.get("username", user_data["email"]),
                first_name=user_data.get("first_name", ""),
                last_name=user_data.get("last_name", ""),
                whatsapp_number=user_data.get("whatsapp_number", ""),
                is_active=True,  # Now activating the user
                is_agent=user_data.get("is_agent", False),
                password=user_data.get("password"),  # Ensure the password is hashed
            )
            if user.is_agent:
                AgentProfile.objects.create(
                    user=user,
                    agency_name=user_data.get("agency_name", ""),
                )
        except Exception as e:
            return self.custom_response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Error during user creation: {str(e)}",
            )

        cache.delete(f"auth_code_{email}")
        cache.delete(f"user_data_{email}")
        return self.custom_response(
            status=status.HTTP_201_CREATED,
            message="Authentication code verified successfully. Your account has been activated.",
        )


class EmailVerifyView(CustomResponseMixin, APIView):
    """
    API endpoint to verify a user's email using a signed token.

    This view confirms email verification and activates the user's account.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        description="Verify user email using the signed token from the email link.",
        parameters=[
            openapi.Parameter(
                name="token",
                type=OpenApiTypes.STR,
                in_="query",
                description="Signed token sent to the user's email for verification.",
                required=True,
            ),
        ],
        responses={
            200: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
            404: NotFoundResponseSerializer,
            500: ErrorResponseSerializer,
        },
    )
    def get(self, request):
        """Verifies the signed token and activates the user account."""
        try:
            token = request.query_params.get("token")
            signer = Signer()
            email = signer.unsign(token)

            user_data = cache.get(f"user_data_{email}")

            if not user_data:
                return self.custom_response(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="User data is missing or expired.",
                )
            try:
                user = User.objects.create_user(
                    email=user_data["email"],
                    username=user_data.get("username", user_data["email"]),
                    first_name=user_data.get("first_name", ""),
                    last_name=user_data.get("last_name", ""),
                    whatsapp_number=user_data.get("whatsapp_number", ""),
                    is_active=True,  # Now activating the user
                    is_agent=user_data.get("is_agent", False),
                    password=user_data.get("password"),  # Ensure the password is hashed
                )
                if user.is_agent:
                    AgentProfile.objects.create(
                        user=user,
                        agency_name=user_data.get("agency_name", ""),
                    )
            except Exception as e:
                return self.custom_response(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message=f"Error during user creation: {str(e)}",
                )

            cache.delete(f"auth_code_{email}")
            cache.delete(f"user_data_{email}")
            agency_name = user_data.get("agency_name")
            contact_info = user_data.get("contact_info")

            if user.is_agent:
                try:
                    AgentProfile.objects.create(
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
    """
    API endpoint to request a password reset email.

    **POST**: Send a password reset email to the user if the email exists.
    """

    permission_classes = [AllowAny]
    serializer_class = ResetPasswordEmailRequestSerializer

    @extend_schema(
        summary="Request Password Reset Email",
        description="Sends a password reset email to the provided email if it exists in the system.",
        request=ResetPasswordEmailRequestSerializer,
        responses={
            201: CreateResponseSerializer,
            404: NotFoundResponseSerializer,
            500: ErrorResponseSerializer,
        },
    )
    def post(self, request):
        """Handles password reset email requests."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        if User.objects.filter(
            email=email
        ).exists():  # Change this construct to get_or_404
            user = User.objects.get(email=email)

            try:
                email_service = EmailService()
                email_service.send_password_reset_email(request, user)
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
    """
    API endpoint to verify password reset token and redirect accordingly.

    **GET**: Validates the password reset token and returns a redirect URL.
    """

    permission_classes = [AllowAny]
    serializer_class = SetNewPasswordSerializer

    @extend_schema(
        summary="Check Password Reset Token",
        parameters=[
            OpenApiParameter(
                name="uidb64",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Base64 encoded user ID",
            ),
            OpenApiParameter(
                name="token",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Password reset token",
            ),
        ],
        responses={200: OpenApiResponse(description="Token is valid.")},
    )
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
    """
    API endpoint to reset a user's password.

    **PATCH**: Accepts new password and resets it.
    """

    permission_classes = [AllowAny]
    serializer_class = SetNewPasswordSerializer

    @extend_schema(
        summary="Reset Password",
        description="Allows users to set a new password using a valid reset token.",
        request=SetNewPasswordSerializer,
        responses={
            200: SuccessResponseSerializer,
            400: ErrorResponseSerializer,
        },
    )
    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.custom_response(
            data={"success": True, "message": "Password reset success"},
        )


class ValidateOTPAndResetPassword(CustomResponseMixin, generics.GenericAPIView):
    """
    API endpoint to validate an OTP and reset the user's password.

    **POST**: Validates the OTP and updates the password.
    """

    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer

    @extend_schema(
        summary="Validate OTP & Reset Password",
        description="Validates a One-Time Password (OTP) and allows the user to reset their password.",
        request=ResetPasswordSerializer,
        responses={
            200: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
            404: NotFoundResponseSerializer,
        },
    )
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
    """
    API endpoint for user login.

    **POST**: Authenticates a user and returns JWT access & refresh tokens.
    """

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(
        summary="User Login",
        description="Authenticates the user and returns an access & refresh token.",
        request=LoginSerializer,
        responses={
            200: SuccessResponseSerializer,
            400: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                "Successful Login",
                value={
                    "message": "Login successful",
                    "data": {
                        "accessToken": "eyJhbGciOiJIUzI1NiIsInR...",
                        "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5...",
                    },
                },
                request_only=False,
                response_only=True,
            ),
            OpenApiExample(
                "Invalid Credentials",
                value={"message": "Invalid email or password"},
                request_only=False,
                response_only=True,
            ),
        ],
    )
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
