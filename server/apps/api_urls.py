# Third Party Modules
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Local Modules - Regular Viewsets
from apps.authentication.views import AuthViewSet

# Local Modules - Admin Viewsets
from apps.coach.views import AdminCoachViewSet, CoachViewSet, EvalViewSet
from apps.core.views import CoachingPhaseVideosViewSet, CoreViewSet
from apps.identities.views import (
    AdminIdentityImageChatViewSet,
    AdminIdentityViewSet,
    IdentityImageChatViewSet,
    IdentityViewSet,
)
from apps.prompts.views import PromptViewSet
from apps.reference_images.views import ReferenceImageViewSet
from apps.test_scenario.views import AdminTestScenarioViewSet
from apps.users.views import AdminTestUserViewSet, UserViewSet

# Initialize routers
default_router = DefaultRouter(trailing_slash=False)
admin_router = DefaultRouter(trailing_slash=False)  # Router for admin-only endpoints
business_router = DefaultRouter(trailing_slash=False)  # router user for documentations
brand_web_router = DefaultRouter(trailing_slash=False)  # brand web

# Register regular viewsets
default_router.register(r"auth", AuthViewSet, basename="auth")
default_router.register(r"prompts", PromptViewSet, basename="prompts")
default_router.register(r"core", CoreViewSet, basename="core")
default_router.register(
    r"core/public/coaching-phase-videos",
    CoachingPhaseVideosViewSet,
    basename="core-public-coaching-phase-videos",
)  # Public Coaching Phase Videos config (feature flag)
default_router.register(r"coach", CoachViewSet, basename="coach")
default_router.register(r"eval", EvalViewSet, basename="eval")
default_router.register(r"user", UserViewSet, basename="user")
default_router.register(r"identities", IdentityViewSet, basename="identities")
default_router.register(
    r"identity-image-chat", IdentityImageChatViewSet, basename="identity-image-chat"
)
default_router.register(
    r"reference-images", ReferenceImageViewSet, basename="reference-images"
)

# Register admin viewsets
# These will be available at /api/v1/admin/{resource}/
admin_router.register(r"coach", AdminCoachViewSet, basename="admin-coach")
admin_router.register(
    r"test-scenarios", AdminTestScenarioViewSet, basename="admin-test-scenarios"
)
admin_router.register(r"identities", AdminIdentityViewSet, basename="admin-identities")
admin_router.register(
    r"identity-image-chat",
    AdminIdentityImageChatViewSet,
    basename="admin-identity-image-chat",
)
admin_router.register(r"test-user", AdminTestUserViewSet, basename="admin-test-user")

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
# Admin endpoints are mounted at /admin/ prefix
# Regular endpoints are at the root level
urlpatterns = (
    default_router.urls
    + [path("admin/", include(admin_router.urls))]
    + auth_paths
    + docs_paths
)
