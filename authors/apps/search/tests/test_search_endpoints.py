import logging

import pytest
from django.utils.http import urlencode
from rest_framework.reverse import reverse

from authors.apps.authentication.tests.factories.authentication import \
    ArticlesFactory

logger = logging.getLogger(__file__)


@pytest.mark.django_db
class TestSearchFilter:
    @staticmethod
    def reverse_querystring(view, urlconf=None, args=None, kwargs=None,
                            current_app=None, query_kwargs=None):
        '''Custom reverse to handle query strings.'''
        base_url = reverse(view, urlconf=urlconf, args=args, kwargs=kwargs,
                           current_app=current_app)
        if query_kwargs:
            return '{}?{}'.format(base_url, urlencode(query_kwargs))

        return base_url

    def test_filter_endpoint_anonymous_user(self, test_client):
        # add an article to the db
        article = ArticlesFactory()
        # view the article
        logger.error(article.title)
        # get the url with query arguments
        url = self.reverse_querystring(
            view='filter-articles',
            query_kwargs={"title": article.title}
        )
        # search the DB
        response = test_client.get(url)
        # display the results
        logger.error(response.data)

        # test assertions
        assert response.status_code == 200
        assert len(response.data) == 1

    def test_filter_endpoint_authenticated_user(self, test_auth_client):
        # add an article to the db
        article = ArticlesFactory()
        # view the article
        logger.error(article.title)
        # get the url with query arguments
        url = self.reverse_querystring(
            view='filter-articles',
            query_kwargs={"title": article.title}
        )
        # search the DB
        response = test_auth_client.get(url)
        # display the results
        logger.error(response.data)

        # test assertions
        assert response.status_code == 200
        assert len(response.data) == 1

    def test_search_the_database(self, test_client):
        # add 3 articles to the db
        article = ArticlesFactory()
        ArticlesFactory()
        ArticlesFactory()

        url = self.reverse_querystring(
            view='search-articles',
            query_kwargs={"title": article.title}
        )
        url = url.replace('+', '%20')
        response = test_client.get(url)

        assert response.status_code == 200
        assert isinstance(response.data, list)
