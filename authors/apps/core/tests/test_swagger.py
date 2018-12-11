import pytest
from rest_framework import status


@pytest.mark.django_db
class TestSwagger:
    """Test swagger UI"""
    def test_swagger_ui(self, test_client):
        response = test_client.get('/')
        assert response.status_code == status.HTTP_200_OK
