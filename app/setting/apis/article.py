from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response

from app.auth.permissions import IsInternalUser
from app.base.pagination import CustomPagination

from app.setting.models import Article
from app.setting.serializers import article as article_serializers
from app.setting.filters.article import ArticleFilter


class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = article_serializers.ArticleSerializer
    permission_classes = [IsInternalUser]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ArticleFilter
    search_fields = ["id", "slug", "title_vi", "title_en", "tags"]
    ordering_fields = ["id", "created_at", "status", "title_vi", "title_en", "slug"]
    ordering = ["-created_at"]
    lookup_field = 'slug'
    
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
