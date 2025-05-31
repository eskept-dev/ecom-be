from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from app.base.pagination import CustomPagination
from app.location import serializers
from app.location.models import Location


class LocationModelViewSet(ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = serializers.LocationSerializer
    pagination_class = CustomPagination

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
