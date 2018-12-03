import pytest
from rest_framework.test import APIClient


@pytest.fixture(scope='session')
def test_client():
    """
    a session wide client to test application endpoints
    :return test_client:
    """
    # a drf api client instance is returned
    client = APIClient()
    yield client  # yield the fixture value
