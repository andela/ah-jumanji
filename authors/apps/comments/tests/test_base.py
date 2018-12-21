import json

from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from authors.apps.authentication.models import User


class TestBase(APITestCase):
    def setUp(self):

        self.user = {
            "user": {
                "username": "test_user",
                "email": "testuser@gmail.com",
                "password": "Test@user1"
            }
        }
        self.comment = {
            "comment": {
                "body": "This is a comment"
            }
        }

        self.updated_comment = {
            "comment": {
                "body": "This is an updated comment"
            }
        }
        self.article = {
            "title": "Test Post",
            "description": "This is a posting test",
            "body": "The test was successful",
            "tagList": "live again"
        }

        # registers and activate them
        self.register_user = self.client.post(
            reverse('register'), data=self.user, format='json')
        user = User.objects.get(email='testuser@gmail.com')
        user.is_active = True
        user.save()

        # logins a user and gets token
        self.login_user = self.client.post(
            reverse('login'), data=self.user, format='json')
        data = self.login_user.content
        self.token = json.loads(data.decode('utf-8'))['user']['token']

        # post an article and get slug
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        self.post_article = self.client.post(
            reverse('articles'), data=self.article, format='json')
        article = self.post_article.content
        self.slug = json.loads(article.decode('utf-8'))['article']['slug']

        # post a comment and get id for updating and deleting
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        self.post_comment = self.client.post(
            reverse(
                'comments',
                kwargs={
                    "slug": self.slug}),
            data=self.comment,
            format='json')
        comment = self.post_comment.content
        self.id = json.loads(comment.decode('utf-8'))['comment']['id']
