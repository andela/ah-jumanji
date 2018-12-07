import pytest
from rest_framework.test import APIClient

from authors.apps.authentication.backends import JWTAuthentication
from authors.apps.authentication.tests.factories.authentication import \
    (UserFactory2, ProfileFactory, FollowerFactory)


@pytest.fixture()
def test_user(db):
    """create a sample user"""
    user = UserFactory2()
    yield user


@pytest.fixture()
def test_user2(db):
    """create a sample user"""
    user = UserFactory2()
    yield user


@pytest.fixture()
def test_profile(db, test_user):
    """create a sample user profile"""
    profile = ProfileFactory(user=test_user)
    yield profile


@pytest.fixture()
def test_profile2(db, test_user2):
    """create a sample user profile"""
    profile = ProfileFactory(user=test_user2)
    yield profile


@pytest.fixture()
def test_following_relation(db, test_user, test_user2):
    """def test follower relationship"""
    following = FollowerFactory(follower=test_user, followed=test_user2)
    yield following


@pytest.fixture()
def test_reversed_following_relation(db, test_user, test_user2):
    """def test follower relationship"""
    following = FollowerFactory(follower=test_user2, followed=test_user)
    yield following


@pytest.fixture()
def test_client():
    """
    a session wide client to test application endpoints
    :return test_client:
    """
    # a drf api client instance is returned
    client = APIClient()
    yield client  # yield the fixture value


@pytest.fixture()
def test_auth_client(test_user):
    """
    a session wide client to test protected application endpoints
    :return client:
    """
    token = JWTAuthentication.generate_token(test_user)
    # a drf api client instance is returned
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    yield client  # yield the fixture value
