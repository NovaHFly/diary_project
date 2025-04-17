from random import choice, choices

from pytest import fixture, mark
from pytest_lazy_fixtures import lf, lfc
from rest_framework import status

from diary.models import Note, Tag

pytestmark = mark.django_db


@fixture
def updated_note_json(
    some_note,
    new_note_data,
    to_local_time,
):
    return {
        'id': some_note.id,
        'created_at': to_local_time(some_note.created_at).isoformat(),
    } | new_note_data


@mark.usefixtures('some_note')
@mark.parametrize(
    ['client', 'url', 'status_code', 'expected_response_content'],
    [
        [
            lf('author_client'),
            lf('note_list_url'),
            status.HTTP_200_OK,
            [lfc('note_to_json', lf('some_note'))],
        ],
        [
            lf('author_client'),
            lf('note_detail_url'),
            status.HTTP_200_OK,
            lfc('note_to_json', lf('some_note')),
        ],
        [
            lf('another_client'),
            lf('note_list_url'),
            status.HTTP_200_OK,
            [],
        ],
        [
            lf('another_client'),
            lf('note_detail_url'),
            status.HTTP_404_NOT_FOUND,
            {'detail': 'No Note matches the given query.'},
        ],
    ],
)
def test_get(
    client,
    url,
    status_code,
    expected_response_content,
):
    response = client.get(url)
    assert response.status_code == status_code
    assert response.json() == expected_response_content


def test_create(
    note_to_json,
    author_client,
    note_list_url,
    new_note_data,
):
    note_count = Note.objects.count()

    response = author_client.post(note_list_url, data=new_note_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert Note.objects.count() - note_count == 1

    new_note = Note.objects.get(title=new_note_data['title'])
    assert response.json() == note_to_json(new_note)


def test_create_note_creates_tags(
    some_user_client,
    note_list_url,
    new_note_data,
):
    assert not Tag.objects.filter(name__in=new_note_data['tags']).exists()

    some_user_client.post(note_list_url, data=new_note_data)

    tags = Tag.objects.filter(name__in=new_note_data['tags'])
    assert tags.exists()
    assert [tag.name for tag in tags] == new_note_data['tags']


def test_prevent_create_duplicate(
    author_client,
    note_list_url,
    new_note_data,
):
    author_client.post(note_list_url, data=new_note_data)

    note_count = Note.objects.count()

    response = author_client.post(note_list_url, data=new_note_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Note.objects.count() == note_count


@mark.parametrize('method', ['put', 'patch'])
@mark.parametrize(
    ['client', 'status_code', 'expected_json'],
    [
        [
            lf('author_client'),
            status.HTTP_200_OK,
            lf('updated_note_json'),
        ],
        [
            lf('another_client'),
            status.HTTP_404_NOT_FOUND,
            lfc('note_to_json', lf('some_note')),
        ],
    ],
)
def test_update(
    note_to_json,
    client,
    note_detail_url,
    method,
    status_code,
    some_note,
    new_note_data,
    expected_json,
):
    request_func = getattr(client, method)
    response = request_func(
        note_detail_url,
        data=new_note_data,
    )
    assert response.status_code == status_code

    new_note = Note.objects.get(id=some_note.id)
    assert note_to_json(new_note) == expected_json
    assert some_note.author == new_note.author


@mark.parametrize(
    ['client', 'status_code', 'deleted_items_count'],
    [
        [lf('author_client'), status.HTTP_204_NO_CONTENT, 1],
        [lf('another_client'), status.HTTP_404_NOT_FOUND, 0],
    ],
)
def test_delete(
    client,
    note_detail_url,
    status_code,
    deleted_items_count,
):
    note_count = Note.objects.count()

    response = client.delete(note_detail_url)
    assert response.status_code == status_code

    assert note_count - Note.objects.count() == deleted_items_count


@mark.usefixtures('create_many_notes')
def test_ordering(author_client, note_list_url):
    response = author_client.get(note_list_url)

    notes = response.json()
    assert notes == sorted(notes, key=lambda x: x['created_at'], reverse=True)


@mark.usefixtures('create_many_notes')
def test_title_filter(author_client, note_list_url):
    query = choice(choice(Note.objects.all()).title)

    response = author_client.get(note_list_url + f'?title={query}')
    response_ids = sorted(item['id'] for item in response.json())
    db_ids = sorted(
        note.id for note in Note.objects.filter(title__contains=query)
    )

    assert response_ids == db_ids


@mark.usefixtures('create_many_notes')
def test_tags_filter(author_client, note_list_url):
    random_tag_names = [
        tag.name for tag in choices(choice(Note.objects.all()).tags.all(), k=2)
    ]

    query = '&'.join(f'tags={name}' for name in random_tag_names)

    response = author_client.get(note_list_url + f'?{query}')
    response_ids = sorted(item['id'] for item in response.json())
    db_ids = sorted(
        {
            note.id
            for note in Note.objects.filter(tags__name__in=random_tag_names)
        }
    )

    assert response_ids == db_ids


@mark.parametrize(
    'url,method',
    [
        [lf('note_list_url'), 'get'],
        [lf('note_list_url'), 'post'],
        [lf('note_detail_url'), 'get'],
        [lf('note_detail_url'), 'put'],
        [lf('note_detail_url'), 'patch'],
        [lf('note_detail_url'), 'delete'],
    ],
)
def test_unauthorized_request(client, url, method):
    request_func = getattr(client, method)
    response = request_func(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
