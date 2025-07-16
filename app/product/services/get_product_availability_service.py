from datetime import date, timedelta
from venv import logger

from django.core.cache import cache

from app.base.service import BaseService

from app.product.models import ProductAvailabilityConfiguration, Product
from app.product.services.compute_product_availability_service import ComputeProductAvailabilityService
from app.product.services.schemas import ComputedProductAvailability


PRODUCT_AVAILABILITY_CONFIGURATION_CACHE_KEY = 'product_availability_configuration'
COMPUTED_PRODUCT_IDS_KEY = 'computed_product_availability:product_ids'
CACHE_TTL = 60 * 60 * 24


class GetProductAvailabilityService(BaseService):
    def __init__(self, product_ids: list[int], start_date: date, end_date: date):
        self.product_ids = product_ids
        self.start_date = start_date
        self.end_date = end_date
        
    def perform(self) -> dict[date, list[ComputedProductAvailability]]:
        if self.can_use_cached_product_availability_configurations():
            return self.get_cached_computed_product_availability_calendars_by_day()
        
        return self.get_computed_product_availability_calendars_by_day()
        
    def get_computed_product_availability_calendars_by_day(self) -> dict[date, list[ComputedProductAvailability]]:
        self.product_availability_configurations = self.list_product_availability_configurations()
        if not self.product_availability_configurations:
            return {}

        self.products = self.get_products()
        self.product_map = {product.id: product for product in self.products}

        computed_product_availability_calendars_by_day: dict[date, list[ComputedProductAvailability]] = {}
        for i in range((self.end_date - self.start_date).days + 1):
            day = self.start_date + timedelta(days=i)
            computed_product_availability_calendars_by_day[day] = []

            for product_id in self.product_ids:
                product = self.product_map.get(product_id)
                if not product:
                    continue

                product_availability_configuration = self.select_effective_product_availability_configuration(product)
                computed_product_availability = ComputeProductAvailabilityService(
                    product=product,
                    product_availability_configuration=product_availability_configuration,
                ).perform()

                computed_product_availability_calendars_by_day[day].append(computed_product_availability)

        self.store_computed_product_availability_calendars_by_day(computed_product_availability_calendars_by_day)

        return computed_product_availability_calendars_by_day
    
    def get_cached_computed_product_availability_calendars_by_day(self) -> dict[date, list[ComputedProductAvailability]]:
        cached_data = cache.get(PRODUCT_AVAILABILITY_CONFIGURATION_CACHE_KEY)

        from app.core.utils.logger import logger
        logger.info(f"Cached data: {cached_data.keys()}")
        
        filtered_time_range_data = {}
        for date, availabilities in cached_data.items():
            if date < self.start_date or date > self.end_date:
                continue
            filtered_time_range_data[date] = availabilities

        for date, availabilities in filtered_time_range_data.items():
            filter_product_availabilities = []
            for availability in availabilities:
                if availability.product.id not in self.product_ids:
                    continue
                filter_product_availabilities.append(availability)
            filtered_time_range_data[date] = filter_product_availabilities

        return filtered_time_range_data

    def store_computed_product_availability_calendars_by_day(self, computed_product_availability_calendars_by_day: dict[date, list[ComputedProductAvailability]]):
        cache.set(
            PRODUCT_AVAILABILITY_CONFIGURATION_CACHE_KEY,
            computed_product_availability_calendars_by_day,
            CACHE_TTL,
        )
        
        cache.set(
            COMPUTED_PRODUCT_IDS_KEY,
            self.product_ids,
            CACHE_TTL,
        )

    def can_use_cached_product_availability_configurations(self) -> bool:
        return self.is_cached_product_ids(self.product_ids) \
            and self.is_cached_date_range(self.start_date, self.end_date)

    def is_cached_product_ids(self, product_ids: list[int]) -> bool:
        cached_computed_product_ids = cache.get(COMPUTED_PRODUCT_IDS_KEY, [])
        if not cached_computed_product_ids:
            return False
        
        return all(product_id in cached_computed_product_ids for product_id in product_ids)
    
    def is_cached_date_range(self, start_date: date, end_date: date) -> bool:
        cached_data = cache.get(PRODUCT_AVAILABILITY_CONFIGURATION_CACHE_KEY, [])
        if not cached_data:
            return False
        
        dates = [date.strftime('%Y-%m-%d') for date in cached_data.keys()]
        return start_date.strftime('%Y-%m-%d') in dates and end_date.strftime('%Y-%m-%d') in dates

    def get_products(self) -> list[Product]:
        return Product.objects.filter(id__in=self.product_ids)

    def list_product_availability_configurations(self) -> list[ProductAvailabilityConfiguration]:
        return ProductAvailabilityConfiguration.objects.filter(
            products__in=self.product_ids,
            start_date__lte=self.end_date,
            end_date__gte=self.start_date,
        ).all()

    def select_effective_product_availability_configuration(self, product: Product) -> ProductAvailabilityConfiguration:
        max_capacity = ProductAvailabilityConfiguration.NO_LIMIT_MAX_CAPACITY
        effective_product_availability_configuration = None
        
        for product_availability_configuration in self.product_availability_configurations:
            computed_product_availability = ComputeProductAvailabilityService(
                product=product,
                product_availability_configuration=product_availability_configuration,
            ).perform()

            if computed_product_availability.max_capacity <= max_capacity:
                effective_product_availability_configuration = product_availability_configuration
                max_capacity = computed_product_availability.max_capacity
        
        return effective_product_availability_configuration
