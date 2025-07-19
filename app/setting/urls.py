from django.urls import include, path
from rest_framework import routers

from app.setting.apis import article as article_apis


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'article', article_apis.ArticleViewSet, basename='article')


urlpatterns = [
    path('', include(router.urls)),
]
