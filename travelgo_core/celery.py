import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travelgo_core.settings')

app = Celery('travelgo_core')
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

from celery.schedules import crontab

app.conf.beat_schedule = {
    'generate-daily-quests-midnight': {
        'task': 'quests.tasks.generate_daily_quests',
        'schedule': crontab(hour=0, minute=0),
    },
}
