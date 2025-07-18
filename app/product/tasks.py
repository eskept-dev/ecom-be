from datetime import datetime
from app.core.celery import celery_app
from app.core.utils.logger import logger
from app.product.services.precompute_product_availability_service import PrecomputeProductAvailabilityService
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


@celery_app.task(name="precompute_product_availability_task")
def precompute_product_availability_task(product_ids: list[int], start_date: str, end_date: str):
    try:
        logger.info("Starting precompute product availability")

        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        logger.info(f"Precompute product availability for {start_date} to {end_date}")

        PrecomputeProductAvailabilityService(
            product_ids=product_ids,
            start_date=start_date,
            end_date=end_date,
        ).perform()

        logger.info("Precompute product availability completed")
    except Exception as e:
        logger.error(f"Error precomputing product availability: {e}")
        raise e
