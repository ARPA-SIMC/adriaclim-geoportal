from celery import shared_task,chain



@shared_task
def task_get_all_data():
    from myFunctions import allFunctions
    # print("get_all_datasets!")
    # Call your function here
    allFunctions.getAllDatasets()


@shared_task
def download_big_data_yearly():
    from myFunctions import allFunctions
    # print("yearly!")
    # Call your function here
    allFunctions.download_big_data("yearly")

@shared_task
def download_big_data_seasonal():
    from myFunctions import allFunctions
    #print("shared_task!")
    # print("seasonal")
    # Call your function here
    allFunctions.download_big_data("seasonal")

@shared_task
def download_big_data_monthly():
    from myFunctions import allFunctions
    #print("shared_task!")
    # print("monthly")
    # Call your function here
    allFunctions.download_big_data("monthly")

@shared_task
def download_all_data():
    #from myFunctions import allFunctions
    # print("shared_task!")
    # Call your function here
    ch = chain(download_big_data_yearly(),download_big_data_seasonal(),download_big_data_monthly())()

