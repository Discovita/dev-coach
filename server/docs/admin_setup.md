# Django Rest Framework Admin Panel Setup Guide

## Overview
This guide provides step-by-step instructions for setting up and configuring the Django Rest Framework Admin Panel in a production environment. The admin panel provides a secure interface for managing your application's data and API resources.

## Prerequisites
- Python 3.x
- PostgreSQL
- Basic understanding of Django and Django Rest Framework

## 1. Dependencies Installation

Install the required packages in your virtual environment:

```bash
pip install Django==5.1.3
pip install djangorestframework==3.15.2
pip install django-cors-headers==4.6.0
pip install whitenoise==6.8.2
pip install psycopg2-binary==2.9.10
pip install django-environ==0.11.2
```

Or add them to your `requirements.txt`:

```plaintext
Django==5.1.3
djangorestframework==3.15.2
django-cors-headers==4.6.0
whitenoise==6.8.2
psycopg2-binary==2.9.10
django-environ==0.11.2
```

Then run:
```bash
pip install -r requirements.txt
```

## 2. Django Settings Configuration

### Core Settings
In your Django settings file (e.g., `settings/common.py`), configure the following:

```python
# Required Applications
INSTALLED_APPS = [
    'django.contrib.admin',  # Django admin
    'django.contrib.auth',   # Authentication
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'rest_framework',        # Django Rest Framework
    'corsheaders',          # CORS headers
    # Your apps here...
]

# Middleware Configuration
MIDDLEWARE = [
    "apps.core.middleware.health_check_middleware.HealthCheckMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

### Security Settings
```python
# CSRF Configuration
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',
    'http://localhost:5174',
    'https://your-domain.com',
]

# CORS Settings
CORS_ALLOW_ALL_ORIGINS = True  # Set to False in production
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
```

### Static Files Configuration
```python
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS = (str(APPS_DIR.path('static')),)
STATIC_ROOT = os.path.join(BASE_DIR, '.staticfiles')

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
```

### Database Configuration
```python
import environ

env = environ.Env()
env.read_env(os.path.join(BASE_DIR, ".env"))

DATABASES = {
    'default': env.db('DJANGO_DATABASE_DEV_URL', default=''),
}
```

## 3. URL Configuration
In your `urls.py`:

```python
from django.contrib import admin
from django.urls import path, re_path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin interface
    re_path(r'^api/v1/', include('apps.api_urls')),  # API endpoints
]
```

## 4. Environment Variables
Create a `.env` file in your project root with these variables:

```plaintext
DJANGO_SECRET_KEY=your-secure-secret-key
DJANGO_DATABASE_DEV_URL=postgres://user:password@localhost:5432/dbname
AWS_ACCESS_KEY_ID=your-aws-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
```

## 5. Initial Setup Commands
Run these commands to set up your database and static files:

```bash
# Create database migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic
```

## 6. Production Deployment Checklist

### Security
- [ ] Set `DEBUG = False` in production
- [ ] Use strong, unique `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set `CORS_ALLOW_ALL_ORIGINS = False`
- [ ] Update `CSRF_TRUSTED_ORIGINS` with production domains
- [ ] Enable HTTPS
- [ ] Set secure password policies

### Performance
- [ ] Configure caching
- [ ] Set up database connection pooling
- [ ] Enable GZip compression
- [ ] Configure proper logging

### Maintenance
- [ ] Set up database backups
- [ ] Configure error monitoring
- [ ] Set up health checks
- [ ] Document deployment process

## 7. Accessing the Admin Panel

- Development: http://localhost:8000/admin/
- Production: https://your-domain.com/admin/

## 8. Best Practices

1. **Security**
   - Regularly update dependencies
   - Use strong passwords
   - Implement rate limiting
   - Enable two-factor authentication if possible

2. **Performance**
   - Optimize database queries
   - Use caching where appropriate
   - Monitor server resources

3. **Maintenance**
   - Regular backups
   - Monitor error logs
   - Keep documentation updated
   - Regular security audits

## Troubleshooting

### Common Issues

1. **Static Files Not Loading**
   - Verify `STATIC_ROOT` configuration
   - Run `collectstatic` command
   - Check file permissions

2. **Database Connection Issues**
   - Verify database credentials
   - Check database server status
   - Confirm network connectivity

3. **Admin Panel Access Issues**
   - Verify superuser credentials
   - Check user permissions
   - Confirm middleware configuration

## Support

For additional support:
- Django Documentation: https://docs.djangoproject.com/
- DRF Documentation: https://www.django-rest-framework.org/
- Django Admin Documentation: https://docs.djangoproject.com/en/stable/ref/contrib/admin/ 