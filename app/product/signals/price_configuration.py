from django.db.models.signals import post_save
from django.dispatch import receiver

from app.core.celery import celery_app
from app.product.models import (
    ProductPriceConfiguration,
)


@receiver(post_save, sender=ProductPriceConfiguration)
def precompute_product_price_by_price_configuration(sender, instance, created, **kwargs):
    celery_app.send_task("precompute_product_price_task")
