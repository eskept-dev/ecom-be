from app.core.celery import celery_app
from app.core.utils.logger import logger
from app.product.services.import_products import import_products


@celery_app.task(name='product.tasks.import_products_task')
def import_products_task():
    logger.info("Importing products")
    import_products()
    logger.info("Imported products")
