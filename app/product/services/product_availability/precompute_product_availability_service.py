from datetime import date, timedelta
from typing import Any, Optional

from django.core.cache import cache

from app.base.service import BaseService

from app.core.utils.logger import logger
from app.product.models import ProductAvailabilityConfiguration, Product
from app.product.services.product_availability.compute_product_availability_service import ComputeProductAvailabilityService
from app.product.schemas import ComputedProductAvailability


class PrecomputeProductAvailabilityService(BaseService):
    CACHE_KEY_PREFIX = "computed_product_availability:by_day"
    CACHE_TTL = 60 * 60 * 24

    def __init__(self, product_ids: list[int], start_date: date = None, end_date: date = None, days: list[date] = None):
        self.product_ids = product_ids
        self.start_date = start_date
        self.end_date = end_date
    
    def perform(self) -> dict[date, list[ComputedProductAvailability]]:
        self.availability_configuration_mapper = self.group_product_availabilities()
        self.products = self.group_products()

        return self.compute_time_range()
                
    def compute_time_range(self) -> dict[date, list[ComputedProductAvailability]]:
        result = {}
        
        day = self.start_date
        while day <= self.end_date:
            result[day] = self.compute_a_day(day)
            day += timedelta(days=1)

        return result
                
    def compute_a_day(self, day: date) -> list[ComputedProductAvailability]:
        result = []
        
        availability_configurations = self.availability_configuration_mapper.get(day, [])

        for product in self.products:
            optimal_availability_configuration = self.select_optimal_availability_configuration(product, availability_configurations)
            if optimal_availability_configuration:
                computed_product_availability = ComputeProductAvailabilityService(
                    product=product,
                    product_availability_configuration=optimal_availability_configuration,
                ).perform()
                result.append(computed_product_availability)
        
        return result

    def group_product_availabilities(self) -> dict[date, list[ProductAvailabilityConfiguration]]:
        product_availabilities = ProductAvailabilityConfiguration.objects.filter(
            product_id__in=self.product_ids,
            day__gte=self.start_date,
            day__lte=self.end_date,
        ).all()

        result = {
            day: []
            for day in product_availabilities.values_list('day', flat=True).distinct()
        }
        for product_availability in product_availabilities:
            result[product_availability.day].append(product_availability)

        return result

    def group_products(self) -> list[Product]:
        return Product.objects.filter(id__in=self.product_ids).all()

    def select_optimal_availability_configuration(self, product: Product, availabilitity_configurations: list[ProductAvailabilityConfiguration]) -> Optional[ProductAvailabilityConfiguration]:
        max_capacity = ProductAvailabilityConfiguration.NO_LIMIT_MAX_CAPACITY
        effective_product_availability_configuration = None
        
        for configuration in availabilitity_configurations:
            logger.info(f"Selecting optimal availability configuration for product: {product.id}")
            logger.info(f"Configuration: {configuration.id}")
            logger.info(f"Configuration product ids: {configuration.product_id}")
            if product.id != configuration.product_id:
                continue

            computed_product_availability = ComputeProductAvailabilityService(
                product=product,
                product_availability_configuration=configuration,
            ).perform()

            if computed_product_availability.max_capacity <= max_capacity:
                effective_product_availability_configuration = configuration
                max_capacity = computed_product_availability.max_capacity
        
        return effective_product_availability_configuration
