import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dataset_translator.settings')

app = Celery('dataset_translator')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
