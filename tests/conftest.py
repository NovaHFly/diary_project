from django.contrib.auth import get_user_model
from pytest import fixture

User = get_user_model()


@fixture
def creative_user():
    return User.objects.create_user('creator')


@fixture
def another_user():
    return User.objects.create_user('another_user')
