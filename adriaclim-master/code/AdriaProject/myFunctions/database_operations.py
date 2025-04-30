import asyncio
from django.db import connection
from Dataset.models import Node, Polygon


def is_database_almost_full(threshold_percentage=90):
    """
    Checks if the database usage exceeds a defined threshold percentage.
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_database_size(current_database()), pg_size_pretty(pg_database_size(current_database()));")
        database_size_bytes, database_size_pretty = cursor.fetchone()

    max_size_bytes = 110 * 1024 * 1024  # 110 MB
    used_percentage = (database_size_bytes / max_size_bytes) * 100

    return used_percentage >= threshold_percentage


async def delete_all(param, **kwargs):
    """
    Asynchronously deletes all records of a specified model.
    """
    if param == "Node":
        await asyncio.to_thread(Node.objects.all().delete)
    elif param == "Polygon":
        dataset_id = kwargs.get("id")
        if dataset_id is not None:
            await asyncio.to_thread(Polygon.objects.filter(dataset_id=dataset_id).delete)
        else:
            await asyncio.to_thread(Polygon.objects.all().delete)


# import asyncio
# from django.db import connection
# from Dataset.models import Node, Indicator, Polygon




# def is_database_almost_full(threshold_percentage=90):
#     # Get the current database size
#     with connection.cursor() as cursor:
#         cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()));")
#         database_size = cursor.fetchone()[0]

#     # Calculate the percentage of database usage
#     # total_size = str(connection.settings_dict['CONN_MAX_AGE'])  # Maximum database size
#     total_size = 110 * 1024  # Maximum database size
#     if ' kB' in database_size:
#         used_percentage = (float(database_size.replace(' kB', '')) / (float(total_size) * 1024)) * 100
#     elif ' MB' in database_size:
#         used_percentage = (float(database_size.replace(' MB', '')) / float(total_size)) * 100
#     elif ' GB' in database_size:
#         used_percentage = (float(database_size.replace(' GB', '')) / (float(total_size) / 1024)) * 100

#     # Check if the database usage exceeds the threshold
#     return used_percentage >= threshold_percentage


# async def delete_all(param, **kwargs):
#     if param == "Node":
#         objects = await asyncio.gather(*[asyncio.to_thread(Node.objects.all)])
#         await asyncio.gather(*[asyncio.to_thread(obj.delete) for obj in objects])
#     elif param == "Polygon":
#         all_polygons = await asyncio.gather(*[asyncio.to_thread(Polygon.objects.all)])
        
        
# # def is_database_almost_full(threshold_percentage=90):
# #     """
# #     Verifica se il database ha raggiunto una soglia di utilizzo definita.
# #     """
# #     with connection.cursor() as cursor:
# #         cursor.execute("SELECT pg_database_size(current_database())")
# #         size = cursor.fetchone()[0]
# #     max_size = 110 * 1024 * 1024  # 110 MB
# #     return (size / max_size) * 100 > threshold_percentage


# # async def delete_all(param, **kwargs):
# #     """
# #     Elimina in modo asincrono tutti i record di Node o Polygon in base al parametro specificato.
# #     """
# #     if param == "Node":
# #         await asyncio.to_thread(Node.objects.all().delete)
# #     elif param == "Polygon":
# #         await asyncio.to_thread(Polygon.objects.filter(dataset_id=kwargs["id"]).delete)


