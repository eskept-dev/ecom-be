from app.core.celery import celery_app
from app.core.utils.logger import logger
from app.supplier import services as supplier_services


@celery_app.task(name='supplier.tasks.import_suppliers_task')
def import_suppliers_task():
    logger.info("Importing suppliers")
    supplier_services.import_suppliers()
    logger.info("Imported products")
