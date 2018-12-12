from django.urls import path
from rest_framework import routers

from authors.apps.search.views import FilterArticlesView, SearchArticlesView

router = routers.DefaultRouter()
router.register('search', SearchArticlesView, base_name="search-articles")

urlpatterns = [
    path('filter/', FilterArticlesView.as_view(), name='filter-articles'),
    path('search/', SearchArticlesView.as_view({'get': 'list'}),
         name="search-articles")
]
