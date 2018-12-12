from drf_haystack.serializers import HaystackSerializer

from authors.apps.search.search_indexes import ArticlesIndex


class ArticleSearchSerializer(HaystackSerializer):
    class Meta:
        """This is the list of indices to be included in this search"""
        index_classes = [ArticlesIndex]
        # this are the fields in the Index that are included in the search
        fields = ['author', 'title', 'tags', 'keywords', 'autocomplete',
                  'pub_date', 'edit_date', 'slug']
        ignore_fields = ["autocomplete"]

        field_aliases = {
            "q": "autocomplete"
        }
