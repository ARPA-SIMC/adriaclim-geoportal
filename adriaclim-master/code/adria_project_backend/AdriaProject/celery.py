import os
import re
import logging
from pathlib import Path
from celery import Celery
from datetime import datetime
from celery.schedules import crontab
from celery.signals import after_setup_logger

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AdriaProject.settings')
app = Celery('AdriaProject',include=['AdriaProject.tasks'])
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


class IgnoreNoisyErrors(logging.Filter):
    def filter(self, record):
        message = record.getMessage()
        ignore_patterns = [
            r"could not convert string to float",
            r"time data 'UTC' does not match format",
            r"Unknown string format: UTC",
        ]
        import re
        return not any(re.search(p, message) for p in ignore_patterns)

@after_setup_logger.connect
def setup_celery_logger(logger, *args, **kwargs):
    logger.addFilter(IgnoreNoisyErrors())