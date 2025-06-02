from django.urls import include, path
from rest_framework import routers

from app.location import views  


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'', views.LocationModelViewSet, basename='location')


urlpatterns = [
    path('search-osm/', views.OpenStreetMapSearchAPIView.as_view(), name='search-osm'),
    path('', include(router.urls)),
]
