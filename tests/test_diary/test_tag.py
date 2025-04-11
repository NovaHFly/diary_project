from django.core.exceptions import ValidationError
from django.db import IntegrityError
from pytest import mark, raises

from diary.constants import MAX_TITLE_LENGTH
from diary.models import Tag

pytestmark = mark.django_db


def test_valid_tag(valid_tag_data):
    Tag.objects.create(**valid_tag_data).full_clean()


def test_long_name(valid_tag_data):
    with raises(
        ValidationError,
        match=r'name.+at most {} characters'.format(MAX_TITLE_LENGTH),
    ):
        Tag.objects.create(
            **valid_tag_data | {'name': 'r' * (MAX_TITLE_LENGTH + 1)}
        ).clean_fields()


def test_empty_name(valid_tag_data):
    with raises(ValidationError, match=r'name.+cannot be blank'):
        Tag.objects.create(**valid_tag_data | {'name': ''}).clean_fields()


def test_duplicate_name_same_user(valid_tag_data):
    Tag.objects.create(**valid_tag_data)
    with raises(
        IntegrityError,
        match=r'UNIQUE constraint failed.+author.+name',
    ):
        Tag.objects.create(**valid_tag_data)


def test_duplicate_name_different_users(valid_tag_data, another_user):
    Tag.objects.create(**valid_tag_data)
    Tag.objects.create(**valid_tag_data | {'author': another_user})
