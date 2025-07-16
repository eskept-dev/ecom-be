from django.db.models.signals import post_save
from django.dispatch import receiver

from app.core.celery import celery_app
from app.product.models import (
    Product,
)


@receiver(post_save, sender=Product)
def precompute_product_price_by_product(sender, instance, created, **kwargs):
    celery_app.send_task(
        "precompute_product_price_by_product_task",
        kwargs={"product_id": instance.id},
    )
