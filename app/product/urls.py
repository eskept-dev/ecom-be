from django.urls import include, path
from rest_framework import routers

from app.product import apis


product_router = routers.DefaultRouter(trailing_slash=False)
product_router.register(r'', apis.ProductModelViewSet, basename='product')

price_configuration_router = routers.DefaultRouter(trailing_slash=False)
price_configuration_router.register(r'', apis.ProductPriceConfigurationModelViewSet, basename='price-configuration')

availability_configuration_router = routers.DefaultRouter(trailing_slash=False)
availability_configuration_router.register(r'', apis.ProductAvailabilityConfigurationModelViewSet, basename='availability-configuration')

urlpatterns = [
    path('availability_configuration/check_availability', apis.GetProductAvailabilityByDateRangeAPIView.as_view(), name='check_availability'),
    
    path('product/unit', apis.ProductUnitAPIView.as_view(), name='product-units'),
    path('price_configuration/preview', apis.ProductPricePreviewAPIView.as_view(), name='price-configuration-preview'),

    path('product/', include(product_router.urls)),

    path('availability_configuration/', include(availability_configuration_router.urls)),
    path('price_configuration/', include(price_configuration_router.urls)),
]
