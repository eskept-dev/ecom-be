from datetime import date

from rest_framework.exceptions import ValidationError

from app.base.service import BaseService
from app.product.models import (
    ProductAvailabilityConfiguration,
    ProductAvailabilityConfigurationType,
)


class BlockProductAvailabilityService(BaseService):
    def __init__(self, product_ids: list[int], start_date: date, end_date: date):
        self.product_ids = product_ids
        self.start_date = start_date
        self.end_date = end_date

    def perform(self):
        if self.check_if_product_availability_is_blocked():
            raise ValidationError("Products are already blocked for the given date range")

        self.block_product_availability()

    def check_if_product_availability_is_blocked(self) -> bool:
        blocked_product_ids = set(
            ProductAvailabilityConfiguration.objects.filter(
                products__id__in=self.product_ids,
                type=ProductAvailabilityConfigurationType.BLOCK,
                start_date__lte=self.start_date,
                end_date__gte=self.end_date,
            )
            .values_list("products__id", flat=True)
            .distinct()
        )

        return len(blocked_product_ids) == len(self.product_ids)

    def block_product_availability(self):
        config = ProductAvailabilityConfiguration.objects.create(
            type=ProductAvailabilityConfigurationType.BLOCK,
            start_date=self.start_date,
            end_date=self.end_date,
        )
        config.products.set(self.product_ids)
