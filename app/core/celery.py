import os
from celery import Celery
from celery.schedules import crontab

from app.core import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.core.settings')

celery_app = Celery(
    'eskept',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    accept_content=settings.CELERY_ACCEPT_CONTENT,
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    broker_connection_retry_on_startup=True,
    result_backend_transport_options={
        'retry_on_startup': True,
    },
    timezone=settings.CELERY_TIMEZONE,
)

celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()

celery_app.conf.beat_schedule = {
    'precompute_product_price_task': {
        'task': 'precompute_product_price_task',
        'schedule': crontab(minute='*/30')
    },
}