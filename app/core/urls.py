from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):  
    return Response(data={"status": "ok"}, status=status.HTTP_200_OK)

api_v1_patterns = [
    path('auth/', include('app.auth.urls')),
    path('booking/', include('app.booking.urls')),
    path('file/', include('app.file.urls')),
    path('location/', include('app.location.urls')),
    path('payment/', include('app.payment.urls')),
    path('product/', include('app.product.urls')),
    path('service/', include('app.service.urls')),
    path('supplier/', include('app.supplier.urls')),
    path('user/', include('app.user.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Health check
    path('health', health_check),

    # API v1 URLs
    path('api/v1/', include(api_v1_patterns)),
    
    # OpenAPI 3 documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
