from random import choices, randint
from string import ascii_letters

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
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
def tag_to_json():
    def _tag_to_json(tag: Tag) -> dict:
        return {'id': tag.id, 'name': tag.name}

    return _tag_to_json


@fixture
def user_to_json():
    def _user_to_json(user: AbstractUser) -> dict:
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }

    return _user_to_json


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
def user_password():
    return 'Som3P@55word'


@fixture
def some_user(user_password):
    return User.objects.create_user(
        username='some_user',
        email='some_user@diary.com',
        password=user_password,
    )


@fixture
def some_user_client(some_user):
    client = APIClient()
    client.force_authenticate(some_user)
    client.user = some_user
    return client


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


@fixture
def users_list_url():
    return reverse('api:user-list')


@fixture
def user_profile_url():
    return reverse('api:user-me')


@fixture
def user_set_username_url():
    return reverse('api:user-set-username')


@fixture
def user_set_password_url():
    return reverse('api:user-set-password')


@fixture
def token_login_url():
    return reverse('api:login')


@fixture
def token_logout_url():
    return reverse('api:logout')
