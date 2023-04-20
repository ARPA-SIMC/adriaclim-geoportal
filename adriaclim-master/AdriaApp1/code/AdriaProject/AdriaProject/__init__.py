from celery import Celery
print("Ci entro in init.py")
#default_app_config = AdriaProjectConfig
#print("default_app_config",default_app_config)
app = Celery('AdriaProject')
app.config_from_object('django.conf:settings', namespace='CELERY')
default_app_config = 'AdriaProject.apps.AdriaProjectConfig'
#app.autodiscover_tasks()