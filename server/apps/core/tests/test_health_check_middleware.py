"""
Tests for apps.core.middleware.health_check_middleware.HealthCheckMiddleware.

Verifies the /health and /readiness endpoints respond correctly
under normal conditions and failure scenarios.
"""

from unittest.mock import MagicMock, patch

from django.http import HttpRequest
from django.test import SimpleTestCase

from apps.core.middleware.health_check_middleware import HealthCheckMiddleware


class HealthCheckMiddlewareTests(SimpleTestCase):
    """Tests for HealthCheckMiddleware."""

    def _get_middleware(self, db_configured=True):
        """Create middleware instance with mocked get_response."""
        mock_get_response = MagicMock()
        with patch("apps.core.middleware.health_check_middleware.settings") as mock_settings:
            mock_settings.DATABASES = {
                "default": {"ENGINE": "django.db.backends.postgresql"}
            } if db_configured else {}
            middleware = HealthCheckMiddleware(mock_get_response)
        return middleware

    def _make_request(self, path, method="GET"):
        request = HttpRequest()
        request.method = method
        request.path = path
        return request

    def test_health_returns_ok(self):
        """GET /health should return 200 OK."""
        middleware = self._get_middleware()
        request = self._make_request("/health")

        response = middleware(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")

    def test_non_health_path_passes_through(self):
        """Non-health paths should be passed to get_response."""
        mock_get_response = MagicMock()
        with patch("apps.core.middleware.health_check_middleware.settings") as mock_settings:
            mock_settings.DATABASES = {"default": {"ENGINE": "postgresql"}}
            middleware = HealthCheckMiddleware(mock_get_response)

        request = self._make_request("/api/v1/users/")
        middleware(request)

        mock_get_response.assert_called_once_with(request)

    def test_post_to_health_passes_through(self):
        """POST /health should pass through (only GET is intercepted)."""
        mock_get_response = MagicMock()
        with patch("apps.core.middleware.health_check_middleware.settings") as mock_settings:
            mock_settings.DATABASES = {"default": {"ENGINE": "postgresql"}}
            middleware = HealthCheckMiddleware(mock_get_response)

        request = self._make_request("/health", method="POST")
        middleware(request)

        mock_get_response.assert_called_once_with(request)

    @patch("apps.core.middleware.health_check_middleware.connections")
    @patch("apps.core.middleware.health_check_middleware.caches")
    def test_readiness_returns_ok_when_db_healthy(self, mock_caches, mock_connections):
        """GET /readiness should return 200 when DB is reachable."""
        middleware = self._get_middleware()
        request = self._make_request("/readiness")

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)
        mock_connections.__iter__ = MagicMock(return_value=iter(["default"]))
        mock_connections.__getitem__ = MagicMock()
        mock_connections["default"].cursor.return_value = mock_cursor
        mock_caches.all.return_value = []

        response = middleware.readiness(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")

    def test_readiness_returns_500_when_db_not_configured(self):
        """GET /readiness should return 500 when DB is not configured."""
        middleware = self._get_middleware(db_configured=False)
        request = self._make_request("/readiness")

        response = middleware.readiness(request)

        self.assertEqual(response.status_code, 500)
        self.assertIn(b"not properly configured", response.content)

    @patch("apps.core.middleware.health_check_middleware.connections")
    def test_readiness_returns_500_on_db_error(self, mock_connections):
        """GET /readiness should return 500 when DB connection fails."""
        middleware = self._get_middleware()
        request = self._make_request("/readiness")

        mock_connections.__iter__ = MagicMock(return_value=iter(["default"]))
        mock_connections.__getitem__ = MagicMock()
        mock_connections["default"].cursor.side_effect = Exception("Connection refused")

        response = middleware.readiness(request)

        self.assertEqual(response.status_code, 500)
        self.assertIn(b"cannot connect to database", response.content)

    @patch("apps.core.middleware.health_check_middleware.connections")
    def test_readiness_returns_500_on_null_db_response(self, mock_connections):
        """GET /readiness should return 500 when SELECT 1 returns None."""
        middleware = self._get_middleware()
        request = self._make_request("/readiness")

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_connections.__iter__ = MagicMock(return_value=iter(["default"]))
        mock_connections.__getitem__ = MagicMock()
        mock_connections["default"].cursor.return_value = mock_cursor

        response = middleware.readiness(request)

        self.assertEqual(response.status_code, 500)
        self.assertIn(b"invalid response", response.content)
