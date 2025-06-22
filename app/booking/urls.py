from django.urls import include, path
from rest_framework import routers

from app.booking import views


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'', views.BookingModelViewSet, basename='booking')
router.register(r'items', views.BookingItemModelViewSet, basename='booking-item')


urlpatterns = [
    path('payment-methods', views.PaymentMethodApiView.as_view(), name='payment-methods'),

    path('', include(router.urls)),
]
