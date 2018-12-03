import factory
from django.contrib.auth import get_user_model


class UserFactory(factory.Factory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: 'test_user%s' % n)
    email = factory.LazyAttribute(lambda o: '%s@email.com' % o.username)
    password = 'Jake123#'
