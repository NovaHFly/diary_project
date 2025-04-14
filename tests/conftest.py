from random import choices, randint
from string import ascii_letters
from typing import Callable

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.timezone import datetime, localtime
from pytest import fixture
from rest_framework.test import APIClient

from diary.models import Note, Tag

User = get_user_model()


@fixture
def to_local_time():
    def _to_local_time(dt: datetime) -> datetime:
        return localtime(dt)

    return _to_local_time


@fixture
def tag_to_json():
    def _tag_to_json(tag: Tag) -> dict:
        return {'id': tag.id, 'name': tag.name}

    return _tag_to_json


@fixture
def note_to_json(to_local_time):
    def _note_to_json(note: Note) -> dict:
        return {
            'id': note.id,
            'title': note.title,
            'text': note.text,
            'created_at': to_local_time(note.created_at).isoformat(),
            'tags': [tag.name for tag in note.tags.all()],
        }

    return _note_to_json


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
def new_tag_data():
    return {'name': 'new_tag'}


@fixture
def new_note_data():
    return {
        'title': 'new_note',
        'text': 'Donec non elit sed augue.',
        'tags': sorted(['new_tag', 'another_tag', 'some_tag']),
    }


@fixture
def some_tag(valid_tag_data):
    return Tag.objects.create(**valid_tag_data)


@fixture
def create_many_tags(creative_user):
    for _ in range(20):
        Tag.objects.create(
            author=creative_user,
            name=''.join(choices(ascii_letters, k=10)),
        )


@fixture
def create_many_notes(creative_user, create_note, create_many_tags):
    tags = Tag.objects.all()
    for _ in range(20):
        note_data = {
            'title': ''.join(choices(ascii_letters, k=10)),
            'text': 'Some text',
            'author': creative_user,
            'tags': choices(tags, k=randint(3, 5)),
        }
        create_note(**note_data)


@fixture
def some_note(valid_note_data, create_note):
    return create_note(**valid_note_data)


@fixture
def tag_list_url():
    return reverse('api:tags-list')


@fixture
def tag_detail_url(some_tag):
    return reverse('api:tags-detail', kwargs={'pk': some_tag.pk})


@fixture
def note_list_url():
    return reverse('api:notes-list')


@fixture
def note_detail_url(some_note):
    return reverse('api:notes-detail', kwargs={'pk': some_note.pk})
