import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from authors.apps.authentication.tests.factories.authentication import \
    MailingListFactory


@pytest.mark.django_db
class TestMailingList:
    def test_get_entire_mailing_list(self, test_auth_client):
        MailingListFactory()
        response = test_auth_client.get(reverse('mailing-list'))
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data['results'], list)

    def test_get_mailing_list_status(self, test_auth_client):
        response = test_auth_client.get(reverse('mailing-list-status'))
        assert response.status_code == status.HTTP_200_OK
        assert 'email_notifications' in response.data
        assert isinstance(response.data['email_notifications'], bool)

    def test_update_mailing_list_status(self, test_auth_client):
        data = {
            "email_notifications": False,
            "push_notifications": True
        }
        response = test_auth_client.put(
            reverse('mailing-list-status'),
            data=data,
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email_notifications'] is False
