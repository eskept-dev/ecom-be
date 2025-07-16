from app.core.celery import celery_app
from app.core.utils.logger import logger
from app.product.services.precompute_product_price_service import PrecomputeProductPriceService


@celery_app.task(name="precompute_product_price_task")
def precompute_product_price_task():
    logger.info("Precomputing product price")
    PrecomputeProductPriceService().perform()
    logger.info("Precomputing product price completed")
    

@celery_app.task(name="precompute_product_price_by_product_task")
def precompute_product_price_by_product_task(product_id: int):
    logger.info("Precomputing product price")
    PrecomputeProductPriceService(product_ids=[product_id]).perform()
    logger.info("Precomputing product price completed")
