from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from accounts.serializers import SignupSerializer, AgentSignupSerializer
from rest_framework import generics, status
from services import (send_signup_verification_email, CustomResponseMixin)



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


