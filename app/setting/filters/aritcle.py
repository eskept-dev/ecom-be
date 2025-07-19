import django_filters

from app.setting.models import Article


class ArticleFilter(django_filters.FilterSet):
    pages = django_filters.ListFilter(method='filter_by_pages')

    class Meta:
        model = Article
        fields = ["status"]
        
    def filter_by_pages(self, queryset, name, value):
        return queryset.filter(pages__contains=value)
