from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter

from app.auth.permissions import IsInternalUser
from app.base.pagination import CustomPagination

from app.setting.models import Article
from app.setting.serializers import article as article_serializers


class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = article_serializers.ArticleSerializer
    permission_classes = [IsInternalUser]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["id", "slug", "title_vi", "title_en", "tags"]
    ordering_fields = ["id", "created_at", "status", "title_vi", "title_en", "slug"]
    ordering = ["-created_at"]
    lookup_field = 'slug'
