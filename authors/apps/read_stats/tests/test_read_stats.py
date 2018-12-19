import json

from django.urls import reverse
from rest_framework.test import APITestCase

from authors.apps.authentication.models import User


class ReadStatsTest(APITestCase):
    """Read stats test class."""

    def setUp(self):
        """Set up read stats tests."""
        self.user = {
            "user": {
                "username": "test_user",
                "email": "testuser@gmail.com",
                "password": "Test@user1"
            }
        }
        self.article = {
            "title": "Test Post",
            "description": "This is a posting test",
            "body": "The test was successful",
            "tagList": "live again"
        }

        # register and activate them
        self.register_user = self.client.post(
            reverse('register'), data=self.user, format='json')
        user = User.objects.get(email='testuser@gmail.com')
        user.is_active = True
        user.save()

        # login a user and gets token
        self.login_user = self.client.post(
            reverse('login'), data=self.user, format='json')
        data = self.login_user.content
        self.token = json.loads(data.decode('utf-8'))['user']['token']

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        # post an article and get slug
        self.post_article = self.client.post(
            reverse('articles'), data=self.article, format='json')
        article = self.post_article.content
        self.slug = json.loads(article.decode('utf-8'))['article']['slug']

        self.read_url = reverse('read', kwargs={'slug': self.slug})
        self.my_reads = reverse('reads')

    def test_read_article(self):
        """Test read an article."""
        res = self.client.get(self.read_url)
        self.assertEqual(200, res.status_code)
        self.assertContains(res, 'success')
        self.assertIn(b"Article 'Test Post' read.", res.content)

    def test_read_article_before_set_read_time(self):
        """Test read an article before read time ends."""
        self.client.get(self.read_url)
        res = self.client.get(self.read_url)
        self.assertEqual(400, res.status_code)
        self.assertIn(b'Read for less time than the read-time.', res.content)

    def test_articles_have_read_count(self):
        """Test read count functionality."""
        self.list_url = reverse('articleSpecific', kwargs={'slug': self.slug})
        res = self.client.get(self.list_url)
        self.assertContains(res, 'read_count')

    def test_user_gets_all_read_articles(self):
        """Test user gets all read articles"""
        res = self.client.get(self.my_reads)
        self.assertEqual(200, res.status_code)
