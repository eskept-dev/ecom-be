from django.urls import include, path
from rest_framework import routers

from app.service import views


router = routers.DefaultRouter(trailing_slash=False)

urlpatterns = [
    path('service/', include(router.urls)),
]
