from django.core.exceptions import ValidationError
from django.db import DataError, IntegrityError
from pytest import mark, raises

from diary.constants import MAX_TITLE_LENGTH

pytestmark = mark.django_db


def test_valid_note(create_note, valid_note_data):
    create_note(**valid_note_data).full_clean()


def test_long_title(create_note, valid_note_data):
    with raises(DataError):
        create_note(
            **valid_note_data | {'title': 'r' * (MAX_TITLE_LENGTH + 1)}
        ).clean_fields()


def test_empty_title(create_note, valid_note_data):
    with raises(ValidationError):
        create_note(**valid_note_data | {'title': ''}).clean_fields()


def test_duplicate_title_same_user(create_note, valid_note_data):
    create_note(**valid_note_data)

    with raises(IntegrityError):
        create_note(**valid_note_data)


def test_duplicate_title_different_users(
    create_note,
    valid_note_data,
    another_user,
):
    create_note(**valid_note_data)
    create_note(**valid_note_data | {'author': another_user})
