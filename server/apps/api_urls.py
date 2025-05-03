# Third Party Modules
from django.conf.urls import include
from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Local Modules
from apps.authentication.views import AuthViewSet
from apps.prompts.views import PromptViewSet

# Local Modules

# Initialize routers
default_router = DefaultRouter(trailing_slash=False)
business_router = DefaultRouter(trailing_slash=False)  # router user for documentations
brand_web_router = DefaultRouter(trailing_slash=False)  # brand web

# Register viewsets
default_router.register(r"auth", AuthViewSet, basename="auth")
default_router.register(r"prompts", PromptViewSet, basename="prompts")

# JWT token URLs
jwt_patterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

auth_paths = [
    # Define additional paths if needed (e.g., auth, docs)
]

docs_paths = [
    # Add documentation paths here if needed
]

# Combine all urlpatterns
urlpatterns = default_router.urls + auth_paths + docs_paths
