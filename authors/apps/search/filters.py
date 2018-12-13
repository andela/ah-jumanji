from django_filters import rest_framework as filters

from authors.apps.articles.models import Articles


class ArticlesFilter(filters.FilterSet):
    # Filter for articles by date published,modified, using ISO 8601 formatted
    # dates
    publish_date = filters.IsoDateTimeFilter(field_name='created')
    modified_date = filters.IsoDateTimeFilter(field_name='modified')

    class Meta:
        model = Articles
        fields = {
            'title': ['exact', 'contains'],
            'slug': ['exact', 'contains'],
            'description': ['exact', 'contains'],
            'body': ['exact', 'contains'],
            'tagList': ['exact', 'contains'],
            'createdAt': ['exact', 'year__gt', 'year__lt'],
            'updatedAt': ['exact', 'year__gt', 'year__lt'],
            'author__username': ['exact', 'contains'],
        }
