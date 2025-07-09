from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework import status
from rest_framework.response import Response

from app.core.utils.logger import logger


class SoftDeleteViewSetMixin(object):
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            obj.soft_delete()
        except Exception as e:
            logger.error(f"Error deleting object: {e}")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
DEFAULT_CACHE_TIME = 60 * 60 * 24

class ListCacheViewSetMixin(object):    
    @method_decorator(cache_page(DEFAULT_CACHE_TIME))
    def list(self, request, *args, **kwargs):
        _list_action = lambda req, *a, **k: super(ListCacheViewSetMixin, self).list(
            req, *a, **k
        )

        if request.query_params.get("search", None):
            return _list_action(request, *args, **kwargs)
        else:
            cached_list_view = cache_page(DEFAULT_CACHE_TIME)(_list_action)
            return cached_list_view(request, *args, **kwargs)


class RetrieveCacheViewSetMixin(object):
    @method_decorator(cache_page(DEFAULT_CACHE_TIME))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
