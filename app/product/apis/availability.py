from rest_framework.views import APIView

from app.auth.permissions import IsInternalUser
from app.product import serializers


class PreviewProductAvailabilityAPIView(APIView):
    permission_classes = [IsInternalUser]
    
    def get(self, request):
        return super().get(request)
