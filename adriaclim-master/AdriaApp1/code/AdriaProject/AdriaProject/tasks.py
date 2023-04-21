from celery import shared_task



@shared_task
def task_get_all_data():
    from myFunctions import allFunctions
    #print("shared_task!")
    # Call your function here
    allFunctions.getAllDatasets()


@shared_task
def download_big_data():
    from myFunctions import allFunctions
    #print("shared_task!")
    # Call your function here
    allFunctions.download_big_data()