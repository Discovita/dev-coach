# Third Party Modules
from django.conf.urls import include
from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# Local Modules
from apps.authentication.views import AuthViewSet
from apps.prompts.views import PromptViewSet
from apps.core.views import CoreViewSet
from apps.coach.views import CoachViewSet
from apps.users.views import UserViewSet, TestUserViewSet
from apps.test_scenario.views import TestScenarioViewSet

# Local Modules

# Initialize routers
default_router = DefaultRouter(trailing_slash=False)
business_router = DefaultRouter(trailing_slash=False)  # router user for documentations
brand_web_router = DefaultRouter(trailing_slash=False)  # brand web

# Register viewsets
default_router.register(r"auth", AuthViewSet, basename="auth")
default_router.register(r"prompts", PromptViewSet, basename="prompts")
default_router.register(r"core", CoreViewSet, basename="core")
default_router.register(r"coach", CoachViewSet, basename="coach")
default_router.register(r"user", UserViewSet, basename="user")
default_router.register(r"test-user", TestUserViewSet, basename="test-user")
default_router.register(r"test-scenarios", TestScenarioViewSet, basename="test-scenarios")

# JWT token URLs
jwt_patterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

auth_paths = [
    # Define additional paths if needed (e.g., auth, docs)
]

docs_paths = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

# Combine all urlpatterns
urlpatterns = default_router.urls + auth_paths + docs_paths
