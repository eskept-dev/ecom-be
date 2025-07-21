from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from app.auth.permissions import IsInternalUser
from app.base.pagination import CustomPagination

from app.setting.filters.article import ArticleFilter
from app.setting.models import Article
from app.setting.serializers import article as article_serializers


class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = article_serializers.ArticleSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ArticleFilter
    search_fields = ["id", "slug", "title_vi", "title_en", "tags"]
    ordering_fields = ["id", "created_at", "status", "title_vi", "title_en", "slug"]
    ordering = ["-created_at"]
    lookup_field = 'slug'
    
    def get_permissions(self):
        if self.action in ["retrieve", "list"]:
            return [AllowAny()]
        return [IsInternalUser()]
    
    @method_decorator(cache_page(60 * 60 * 24, key_prefix="article_list"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(60 * 60 * 24, key_prefix="article_retrieve"))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @classmethod
    def clear_cache(cls):
        prefixes = [
            "article_list",
            "article_retrieve",
        ]
        
        for prefix in prefixes:
            keys = cache.keys(f"*{prefix}*")
            cache.delete_many(keys)

    def create(self, request, *args, **kwargs):
        self.clear_cache()
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.clear_cache()
        return super().update(request, *args, **kwargs)
        
    def destroy(self, request, *args, **kwargs):
        self.clear_cache()
        return super().destroy(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        self.clear_cache()
        return super().partial_update(request, *args, **kwargs)
    
    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, *args, **kwargs):
        article = self.get_object()
        article.publish()
        return Response(status=status.HTTP_200_OK)
    
    @action(detail=True, methods=["post"], url_path="unpublish")
    def unpublish(self, request, *args, **kwargs):
        article = self.get_object()
        article.unpublish()
        return Response(status=status.HTTP_200_OK)
