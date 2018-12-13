import factory
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from factory import fuzzy

from authors.apps.articles.models import Articles
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
    password = 'Jake123#'
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


class ArticlesFactory(factory.DjangoModelFactory):
    """Generate instances of articles in the DB"""

    class Meta:
        model = Articles
        django_get_or_create = ('author', 'title')

    title = fuzzy.FuzzyText(length=20, prefix='title ', suffix=' text')
    description = fuzzy.FuzzyText(length=20, prefix='description ', )
    body = fuzzy.FuzzyText(length=200, prefix='body ', suffix=' text')
    tagList = fuzzy.FuzzyChoice(['music', 'tech', 'lifestyle', 'money'])
    slug = slugify(title)
    author = factory.SubFactory(UserFactory2)
