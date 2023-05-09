
# from django.apps import AppConfig
# from django.conf import settings
# from django.core.management import call_command
# from myFunctions import allFunctions
# #frm


# class AdriaProjectConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'AdriaProject'
#     print("Ci entro in AdriaProjectConfig")

#     def ready(self):
#         print("Ci entro in ready")
#         allFunctions.getAllDatasets()

    # def ready(self):
    #     # Call your function here
    #     print("Ci entro in ready")
    #     if not settings.ALREADY_POPULATED:
    #         call_command('populate')
    #         settings.ALREADY_POPULATED = True
        
    #     if settings.ALREADY_POPULATED:
    #         print("Ci entro!!!")
    #         allFunctions.getAllDatasets()

    # def __init__(self):
    #     print("Ci entro in init")
    #     # super().__init__()
        