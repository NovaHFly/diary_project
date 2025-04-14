from random import choices, randint
from string import ascii_letters

from django.urls import reverse
from django.utils.timezone import datetime, localtime
from pytest import fixture

from diary.models import Note, Tag


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
