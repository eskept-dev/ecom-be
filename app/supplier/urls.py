from django.urls import include, path
from rest_framework import routers

from app.supplier import views  


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'', views.SupplierModelViewSet, basename='supplier')


urlpatterns = [
    path('supplier/', include(router.urls)),
]
