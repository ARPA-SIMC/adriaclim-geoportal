from celery import shared_task,chain



@shared_task
def task_get_all_data():
    from myFunctions import allFunctions
    allFunctions.getAllDatasets()

@shared_task
def download_big_data_yearly():
    try:
        from myFunctions import allFunctions
        allFunctions.download_big_data("yearly")
    except Exception as e:
        print("Errore TASK =", e)

@shared_task
def download_big_data_seasonal():
    from myFunctions import allFunctions
    allFunctions.download_big_data("seasonal")

@shared_task
def download_big_data_monthly():
    from myFunctions import allFunctions
    allFunctions.download_big_data("monthly")

@shared_task
def download_all_data():
    ch = chain(download_big_data_yearly(),download_big_data_seasonal(),download_big_data_monthly())()

