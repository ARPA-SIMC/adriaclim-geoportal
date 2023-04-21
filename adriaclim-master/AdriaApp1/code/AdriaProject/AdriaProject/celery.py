import os
from celery import Celery
from celery.schedules import crontab

 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AdriaProject.settings')
app = Celery('AdriaProject',include=['AdriaProject.tasks'])
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):

#     # Executes every day at 17:50 a.m.
#     sender.add_periodic_task(
#         crontab(hour=8, minute=45),
#         allDatasets.s(),
#     )

# @app.task
# def allDatasets():
#     from myFunctions import allFunctions
#     allFunctions.getAllDatasets()