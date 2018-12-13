# Create your views here.
import logging

from django_filters.rest_framework import DjangoFilterBackend
from drf_haystack.filters import HaystackAutocompleteFilter
from drf_haystack.viewsets import HaystackViewSet
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from authors.apps.articles.models import Articles
from authors.apps.articles.serializers import BasicArticleSerializer
from authors.apps.search.filters import ArticlesFilter
from authors.apps.search.serializers import ArticleSearchSerializer

logger = logging.getLogger(__name__)


class FilterArticlesView(ListAPIView):
    """A view to search"""
    permission_classes = (AllowAny,)
    queryset = Articles.objects.all()
    serializer_class = BasicArticleSerializer
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = ArticlesFilter


class SearchArticlesView(HaystackViewSet):
    permission_classes = (AllowAny,)
    index_models = [Articles]
    serializer_class = ArticleSearchSerializer
    filter_backends = [HaystackAutocompleteFilter]
