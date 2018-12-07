import factory
from django.contrib.auth import get_user_model

from authors.apps.profiles.models import Profile, Following


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ('username',)

    username = factory.Sequence(lambda n: 'test_user%s' % n)
    email = factory.LazyAttribute(lambda o: '%s@email.com' % o.username)
    password = factory.Faker('password')


class ProfileFactory(factory.DjangoModelFactory):
    class Meta:
        model = Profile
        django_get_or_create = ('user',)

    user = factory.SubFactory(UserFactory)


class FollowerFactory(factory.DjangoModelFactory):
    class Meta:
        model = Following

    follower = factory.SubFactory(UserFactory)
    followed = factory.SubFactory(UserFactory)
