from django.core.cache import cache

from app.base.service import BaseService


class CleanCachedProductAPIService(BaseService):
    def perform(self):
        key_prefix = [
            "product_list",
            "product_retrieve",
        ]

        for key_prefix in key_prefix:
            keys = cache.keys(f"*{key_prefix}*")
            cache.delete_many(keys)
