from django.http import HttpResponse, HttpResponseServerError
from django.db import connections
from django.core.cache import caches
from django.core.cache.backends.memcached import BaseMemcachedCache
from django.conf import settings

#                 Configure Logging
# ★══════════════════════════════════════════════════★
import logging
from logs import logger

logger.configure_logging(__name__)
log = logging.getLogger(__name__)


class HealthCheckMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        self.checks = {
            "/readiness": self.readiness,
            "/health": self.health,
        }
        # Add initialization check
        self._is_database_configured = False
        try:
            if settings.DATABASES and settings.DATABASES.get("default", {}).get(
                "ENGINE"
            ):
                self._is_database_configured = True
        except Exception as e:
            log.warning(
                f"Database not configured during middleware initialization: {e}"
            )

    def __call__(self, request):
        if request.method == "GET" and request.path in self.checks:
            return self.checks[request.path](request)
        return self.get_response(request)

    @staticmethod
    def health(request):
        """
        Returns that the server is alive.
        """
        log.debug("Server is healthy")
        return HttpResponse("OK")

    def readiness(self, request):
        # First check if database is configured
        if not self._is_database_configured:
            log.error("Database is not properly configured in settings")
            return HttpResponseServerError("db: settings not properly configured")

        # Connect to each database and do a generic standard SQL query
        try:
            for name in connections:
                cursor = connections[name].cursor()
                cursor.execute("SELECT 1;")
                row = cursor.fetchone()
                if row is None:
                    log.error(f"Database {name} returned invalid response")
                    return HttpResponseServerError("db: invalid response")
        except Exception as e:
            log.exception(f"Database connection error: {e}")
            return HttpResponseServerError("db: cannot connect to database.")

        # Check memcached connections
        try:
            for cache in caches.all():
                if isinstance(cache, BaseMemcachedCache):
                    stats = cache._cache.get_stats()
                    if len(stats) != len(cache._servers):
                        log.error("Cache connection error")
                        return HttpResponseServerError(
                            "cache: cannot connect to cache."
                        )
        except Exception as e:
            log.exception(f"Cache error: {e}")
            return HttpResponseServerError("cache: cannot connect to cache.")

        log.debug("Server is Ready")
        return HttpResponse("OK")
