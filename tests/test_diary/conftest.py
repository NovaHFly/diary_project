from pytest import fixture

from diary.models import Tag


@fixture
def valid_tag_data(creative_user):
    return {
        'name': 'some_tag',
        'author': creative_user,
    }


@fixture
def some_tag(valid_tag_data):
    return Tag.objects.create(**valid_tag_data)


@fixture
def valid_note_data(creative_user, some_tag):
    return {
        'author': creative_user,
        'title': 'some title',
        'text': 'Lorem ipsum dolor sit amet',
        'tags': [some_tag],
    }
