from app.core.celery import celery_app
from app.core.utils.logger import logger
from app.location import services as location_services


@celery_app.task(name='location.tasks.import_airports_task')
def import_airports_task():
    logger.info("Importing airports")
    location_services.import_airports()
    logger.info("Imported airports")


@celery_app.task(name='location.tasks.import_hotels_task')
def import_hotels_task():
    logger.info("Importing hotels")
    location_services.import_hotels()
    logger.info("Imported hotels")
