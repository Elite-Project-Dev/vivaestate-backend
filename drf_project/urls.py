"""
URL configuration for drf_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Real Estate SAAS Documentation",
        default_version="v1",
        description="API documentation for your Django project",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="olamoyegunolamidesammy@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path("", schema_view.with_ui("swagger", cache_timeout=0), name="swagger-ui"),
    path("admin/", admin.site.urls),
    path("v1/account/", include("apps.accounts.v1.urls")),
    path("social-auth/", include("allauth.urls")),
    path("v1/property/", include("apps.properties.v1.urls")),
    path("v1/social/", include("apps.social.v1.urls")),
    path("v1/subscription/", include("apps.subscription.v1.urls")),
    path("v1/leads/", include("apps.agent_crm.v1.urls")),
    path("v1/ai-assistant", include("apps.ai_assistant.v1.urls")),
    path(
        "swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger-ui"
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="redoc"),
]
