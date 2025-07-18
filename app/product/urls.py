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
    path('availability_configuration/check_product_availability', apis.CheckProductAvailabilityAPIView.as_view(), name='check_product_availability'),
    path('availability_configuration/check_time_range_availability', apis.CheckTimeRangeAvailabilityAPIView.as_view(), name='check_time_range_availability'),
    path('availability_configuration/block', apis.BlockProductAvailabilityAPIView.as_view(), name='block-availability'),
    path('availability_configuration/unblock', apis.UnblockProductAvailabilityAPIView.as_view(), name='unblock-availability'),
    path('availability_configuration/bulk', apis.CreateBulkProductAvailabilityConfigurationAPIView.as_view(), name='create-bulk-availability'),

    path('product/unit', apis.ProductUnitAPIView.as_view(), name='product-units'),
    path('price_configuration/preview', apis.ProductPricePreviewAPIView.as_view(), name='price-configuration-preview'),

    path('product/', include(product_router.urls)),

    path('availability_configuration/', include(availability_configuration_router.urls)),
    path('price_configuration/', include(price_configuration_router.urls)),
]
