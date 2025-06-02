from app.core.celery import celery_app
from app.core.utils.logger import logger
from app.product import services as product_services


@celery_app.task(name='product.tasks.import_products_task')
def import_products_task():
    logger.info("Importing products")
    product_services.import_products()
    logger.info("Imported products")
