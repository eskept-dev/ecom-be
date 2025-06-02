from django.urls import include, path
from rest_framework import routers

from app.product import views  


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'', views.ProductModelViewSet, basename='product')


urlpatterns = [
    path('', include(router.urls)),
]
