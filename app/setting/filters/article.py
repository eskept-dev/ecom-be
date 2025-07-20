import django_filters

from app.setting.models import Article


class ArticleFilter(django_filters.FilterSet):
    statuses = django_filters.CharFilter(method='filter_by_statuses')

    class Meta:
        model = Article
        fields = ["statuses"]
        
    def filter_by_statuses(self, queryset, name, value):
        statuses = value.split(",")
        return queryset.filter(status__in=statuses)
