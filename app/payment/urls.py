from django.urls import path, include
from rest_framework import routers

from app.payment import views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'transaction', views.PaymentTransactionModelViewSet, basename='payment-transaction')


urlpatterns = [
    path('payment/methods', views.PaymentMethodAPIView.as_view(), name='payment-methods'),

    path('payment', include(router.urls)),
]