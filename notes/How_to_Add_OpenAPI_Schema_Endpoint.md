# How to Add an OpenAPI Schema Endpoint to a Django App (drf-spectacular)

This guide explains how to add a [drf-spectacular](https://drf-spectacular.readthedocs.io/) OpenAPI schema endpoint to every new Django app in the Discovita Dev Coach project. It follows the project's versioned API structure and ensures all schema endpoints are consistently exposed under `/api/v1/`.

---

## Why Add an OpenAPI Schema Endpoint?
- **Automatic Type Generation:** Enables frontend teams to generate TypeScript types from backend models/serializers.
- **API Documentation:** Provides up-to-date, interactive API docs (Swagger UI).
- **Consistency:** Ensures all apps expose their schema in a predictable, versioned location.

---

## Step-by-Step Instructions

### 1. Install drf-spectacular

In your backend environment:

```sh
pip install drf-spectacular
```

Add `'drf_spectacular'` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    # ... existing apps ...
    'drf_spectacular',
]
```

---

### 2. Configure drf-spectacular in Django Settings

In your `settings.py`, add:

```python
REST_FRAMEWORK = {
    # ... your other settings ...
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Discovita Dev Coach API',
    'DESCRIPTION': 'API schema for Discovita Dev Coach',
    'VERSION': '1.0.0',
    # Add more settings as needed
}
```

---

### 3. Add Schema Endpoint to Your App's API URLs

**Always add schema endpoints to your app's `api_urls.py` (not the project root `urls.py`).**

#### a. Import drf-spectacular Views

At the top of your `server/apps/api_urls.py`:

```python
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
```

#### b. Add Schema and Swagger UI Endpoints

Add these to your `docs_paths` list:

```python
docs_paths = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
```

#### c. Confirm urlpatterns

Your `urlpatterns` should include all routers and docs paths:

```python
urlpatterns = default_router.urls + auth_paths + docs_paths
```

---

### 4. No Changes Needed in Project Root URLs

Your `server/urls.py` should already include the app's API URLs under a versioned prefix (e.g., `api/v1/`). No changes are needed here.

---

### 5. Verify the Schema Endpoint

1. Run your Django server:
   ```sh
   python manage.py runserver
   ```
2. Visit `http://localhost:8000/api/v1/schema/` to see the raw OpenAPI JSON.
3. Visit `http://localhost:8000/api/v1/docs/` for the interactive Swagger UI.

---

### 6. Use the Schema Endpoint for TypeScript Type Generation

In your frontend project, generate types with:

```sh
npx openapi-typescript http://localhost:8000/api/v1/schema/ --output src/types/api-types.ts
```

---

## Best Practices
- **Always add schema endpoints to each new app's `api_urls.py`.**
- **Keep your API versioning consistent (e.g., `/api/v1/`).**
- **Regenerate TypeScript types after backend changes.**
- **Document the endpoint in your app's README if needed.**

---

## Example: Minimal `api_urls.py` with Schema Endpoint

```python
from django.urls import path
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# ... import your viewsets ...

default_router = DefaultRouter(trailing_slash=False)
# default_router.register(...)

docs_paths = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

urlpatterns = default_router.urls + docs_paths
```

---

**By following these steps for every new Django app, you ensure consistent, discoverable, and up-to-date API documentation and type safety across your project.** 