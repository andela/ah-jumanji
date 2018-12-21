from rest_framework.reverse import reverse
from rest_framework import status
import logging
import json

# local imports
from .test_base import TestBase
logger = logging.getLogger(__file__)


class TestRatings(TestBase):
    ''' Ratings test cases '''

    def test_post_rating(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.rater_token)
        response = self.client.post(
            reverse(
                'ratings',
                kwargs={
                    "slug": self.slug}),
            data=self.rating,
            format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            json.loads(
                response.content.decode('utf-8'))['message'],
            "Rating added successfully")

    def test_post_bad_rating(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.rater_token)
        response = self.client.post(
            reverse(
                'ratings',
                kwargs={
                    "slug": self.slug}),
            data=self.bad_rating,
            format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(
                response.content.decode('utf-8'))['errors']['rating'],
            ['"10" is not a valid choice.'])

    def test_article_author_cannot_rate(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' +
            self.author_token)
        response = self.client.post(
            reverse(
                'ratings',
                kwargs={
                    "slug": self.slug}),
            data=self.rating,
            format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            json.loads(
                response.content.decode('utf-8'))['message'],
            "You cannot rate your own article")

    def test_get_average_rating(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' +
            self.author_token)
        response = self.client.get(
            reverse(
                'ratings',
                kwargs={
                    "slug": self.slug
                }),
            format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            json.loads(
                response.content.decode('utf-8'))['rating'],
            5.0)

    def test_delete_rating(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.rater_token)
        response = self.client.delete(
            reverse(
                'delete_rating',
                kwargs={
                    "slug": self.slug,
                    "id": self.id
                }),
            format='json')
        logger.error(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            json.loads(
                response.content.decode('utf-8'))['message'],
            "Rating removed successfully")

    def test_article_not_found_rate(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.rater_token)
        response = self.client.post(
            reverse(
                'ratings',
                kwargs={
                    "slug": "not-found"}),
            data=self.rating,
            format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            json.loads(
                response.content.decode('utf-8'))['detail'],
            "Article Not found")

    def test_delete_rating_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.rater_token)
        response = self.client.delete(
            reverse(
                'delete_rating',
                kwargs={
                    "slug": self.slug,
                    "id": 12
                }),
            format='json')
        logger.error(response.content)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            json.loads(
                response.content.decode('utf-8'))['detail'],
            "Rating Not found")
