# Create your search Indexes here.
"""
This file contains search indexes for Haystack.
SearchIndex objects are the way Haystack determines what data should be placed
 in the search index and handles the flow of data in.
"""
import datetime

from haystack import indexes
from authors.apps.articles.models import Articles


class ArticlesIndex(indexes.SearchIndex, indexes.Indexable):
    """
    This class contains the Search Index for Articles
    """
    text = indexes.CharField(document=True, use_template=False)
    author = indexes.CharField(model_attr="author")
    title = indexes.CharField(model_attr="title")
    tags = indexes.CharField(model_attr="tagList")
    keywords = indexes.CharField(model_attr="body")
    slug = indexes.CharField(model_attr="slug")
    pub_date = indexes.CharField(model_attr='createdAt')
    edit_date = indexes.CharField(model_attr='updatedAt')

    @staticmethod
    def prepare_author(obj):
        """return the username or blank"""
        return '' if not obj.author else obj.author.username

    @staticmethod
    def prepare_autocomplete(obj):
        return " ".join((
            obj.author.username, obj.title, obj.description
        ))

    def get_model(self):
        """defines the model to be indexed"""
        return Articles

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(
            createdAt__lte=datetime.datetime.now())
