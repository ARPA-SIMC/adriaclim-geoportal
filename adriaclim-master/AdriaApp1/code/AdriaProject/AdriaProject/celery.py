from datetime import datetime
import os
from celery import Celery
from pathlib import Path
from celery.schedules import crontab

 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AdriaProject.settings')
app = Celery('AdriaProject',include=['AdriaProject.tasks'])
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
