import os
from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fully_featured.settings")
app = Celery("fully_featured")
app.config_from_object(settings, namespace="CELERY")
app.autodiscover_tasks()

app.conf.task_routes = {"fully_featured.core.tasks.*": {"queue": "send_completion_to_user"}}
