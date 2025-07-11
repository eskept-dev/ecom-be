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
