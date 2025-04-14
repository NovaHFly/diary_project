from typing import Callable

from django.contrib.auth import get_user_model
from pytest import fixture
from rest_framework.test import APIClient

from diary.models import Note, Tag

User = get_user_model()


@fixture
def create_note() -> Callable[..., Note]:
    def _create_note(**note_data) -> Note:
        tags = note_data.pop('tags')
        note = Note.objects.create(**note_data)
        note.tags.set(tags)
        return note

    return _create_note


@fixture
def creative_user():
    return User.objects.create_user('creator')


@fixture
def another_user():
    return User.objects.create_user('another_user')


@fixture
def author_client(creative_user):
    client = APIClient()
    client.force_authenticate(creative_user)
    return client


@fixture
def another_client(another_user):
    client = APIClient()
    client.force_authenticate(another_user)
    return client


@fixture
def valid_tag_data(creative_user):
    return {
        'name': 'some_tag',
        'author': creative_user,
    }


@fixture
def valid_note_data(creative_user, some_tag):
    return {
        'author': creative_user,
        'title': 'some title',
        'text': 'Lorem ipsum dolor sit amet',
        'tags': [some_tag],
    }


@fixture
def some_tag(valid_tag_data):
    return Tag.objects.create(**valid_tag_data)


@fixture
def some_note(valid_note_data, create_note):
    return create_note(**valid_note_data)
