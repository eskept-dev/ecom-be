from django.urls import include, path
from rest_framework import routers

from app.user import views  


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'', views.UserModelViewSet, basename='user')
    
urlpatterns = [
    path('', include(router.urls)),
]
