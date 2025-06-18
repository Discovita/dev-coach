import os
from celery import Celery
from django.conf import settings

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "settings.local"
)  # or 'settings.production' as needed

print(f"CELERY_BROKER_URL seen by celery worker: {settings.CELERY_BROKER_URL}")
print(
    f"DJANGO_SETTINGS_MODULE seen by celery worker: {os.environ.get('DJANGO_SETTINGS_MODULE')}"
)


app = Celery("server")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
