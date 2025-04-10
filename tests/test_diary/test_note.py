from django.core.exceptions import ValidationError
from django.db import IntegrityError
from pytest import mark, raises

from diary.models import Note

pytestmark = mark.django_db


def create_note(**note_data) -> Note:
    tags = note_data.pop('tags')
    note = Note.objects.create(**note_data)
    note.tags.set(tags)
    return note


def test_valid_note(valid_note_data):
    create_note(**valid_note_data).full_clean()


def test_long_title(valid_note_data):
    with raises(ValidationError, match=r'title.+at most 100 characters'):
        create_note(**valid_note_data | {'title': 'r' * 101}).clean_fields()


def test_empty_title(valid_note_data):
    with raises(ValidationError, match=r'title.+cannot be blank'):
        create_note(**valid_note_data | {'title': ''}).clean_fields()


def test_duplicate_title_same_user(valid_note_data):
    create_note(**valid_note_data)

    with raises(
        IntegrityError,
        match=r'UNIQUE constraint failed.+author.+title',
    ):
        create_note(**valid_note_data)


def test_duplicate_title_different_users(
    valid_note_data,
    another_user,
):
    create_note(**valid_note_data)
    create_note(**valid_note_data | {'author': another_user})
