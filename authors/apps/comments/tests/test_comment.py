import logging

from rest_framework.reverse import reverse
from rest_framework import status
from .test_base import TestBase

logger = logging.getLogger(__file__)


class TestComments(TestBase):

    def test_post_comment(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.post(
            reverse(
                'comments',
                kwargs={
                    "slug": self.slug}),
            data=self.comment,
            format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(b'This is a comment', response.content)

    def test_get_comment(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.get(
            reverse(
                'comments', kwargs={
                    "slug": self.slug}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_comment(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.put(
            reverse(
                'specific-comment',
                kwargs={
                    "slug": self.slug,
                    "id": self.id}),
            data=self.updated_comment,
            format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b'This is an updated comment', response.content)

    def test_delete_comment(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.delete(
            reverse(
                'specific-comment',
                kwargs={
                    "slug": self.slug,
                    "id": self.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_no_article_found_post_comment(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.post(
            reverse(
                'comments',
                kwargs={
                    "slug": "test-slug"}),
            data=self.comment,
            format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(b'Article Not found', response.content)

    def test_no_comment_found_update(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.put(
            reverse(
                'specific-comment',
                kwargs={
                    "slug": self.slug,
                    "id": 10}),
            data=self.updated_comment,
            format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(b'Comment does not exist', response.content)

    def test_no_comment_found_delete(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.delete(
            reverse(
                'specific-comment',
                kwargs={
                    "slug": self.slug,
                    "id": 10}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(b'Comment does not exist', response.content)
