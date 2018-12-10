import factory
from django.contrib.auth import get_user_model

from authors.apps.profiles.models import Profile, Following


class UserFactory(factory.Factory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: 'test_user%s' % n)
    email = factory.LazyAttribute(lambda o: '%s@email.com' % o.username)
    password = 'Jake123#'


class UserFactory2(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ('username',)

    username = factory.Sequence(lambda n: 'test_user%s' % n)
    email = factory.LazyAttribute(lambda o: '%s@email.com' % o.username)
    password = factory.Faker('password')
    is_active = True


class ProfileFactory(factory.DjangoModelFactory):
    class Meta:
        model = Profile
        django_get_or_create = ('user',)

    user = factory.SubFactory(UserFactory)


class FollowerFactory(factory.DjangoModelFactory):
    class Meta:
        model = Following
        django_get_or_create = ('follower', 'followed')

    follower = factory.SubFactory(UserFactory2)
    followed = factory.SubFactory(UserFactory2)
