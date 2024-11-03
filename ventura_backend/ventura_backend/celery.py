# ventura_backend/celery.py

import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ventura_backend.settings")
app = Celery("ventura_backend")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.update(
    broker_connection_retry_on_startup=True,
    worker_concurrency=2,  # Adjust the number of worker processes as needed
)