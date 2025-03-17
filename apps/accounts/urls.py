from django.urls import path

from .views import (AgentSignupView, EmailVerifyView, LoginView,
                    PasswordTokenCheckAPI, ResendEmailView, UserSignupView,
                    VerifyCodeView)

urlpatterns = [
    path("agent/signup/", AgentSignupView.as_view(), name="agent-signup"),
    path("user/signup/", UserSignupView.as_view(), name="user-signup"),
    path("email-verify/", EmailVerifyView.as_view(), name="email-verify"),
    path(
        "resend-auth-code/",
        ResendEmailView.as_view(),
        name="resend_auth_code",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        PasswordTokenCheckAPI.as_view(),
        name="password-reset-confirm",
    ),
    path('password-reset-confirm/<str:uidb64>/<str:token>/', PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),

    path("verify-code/", VerifyCodeView.as_view(), name="verify-signup-code"),
    path("login/", LoginView.as_view(), name="login")
]
