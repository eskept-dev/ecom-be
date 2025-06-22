from django.urls import path

from app.payment import views


urlpatterns = [
    path('methods', views.PaymentMethodAPIView.as_view(), name='payment-methods'),
]