from django.urls import include, path
from rest_framework import routers

from app.user import views  


user_router = routers.DefaultRouter(trailing_slash=False)
user_router.register(r'', views.UserModelViewSet, basename='user')

customer_router = routers.DefaultRouter(trailing_slash=False)
customer_router.register(r'', views.CustomerModelViewSet, basename='customer')

urlpatterns = [
    path('user/', include(user_router.urls)),
    path('customer/', include(customer_router.urls)),
]
