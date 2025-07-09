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




