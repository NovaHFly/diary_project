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


@fixture
def updated_tag_json(
    some_tag,
    new_tag_data,
):
    return {'id': some_tag.id} | new_tag_data


@mark.usefixtures('some_note', 'some_tag')
@mark.parametrize(
    'client,url,status_code,expected_response_content',
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
        [
            lf('author_client'),
            lf('tag_list_url'),
            status.HTTP_200_OK,
            [lfc('tag_to_json', lf('some_tag'))],
        ],
        [
            lf('author_client'),
            lf('tag_detail_url'),
            status.HTTP_200_OK,
            lfc('tag_to_json', lf('some_tag')),
        ],
        [
            lf('another_client'),
            lf('tag_list_url'),
            status.HTTP_200_OK,
            [],
        ],
        [
            lf('another_client'),
            lf('tag_detail_url'),
            status.HTTP_404_NOT_FOUND,
            {'detail': 'No Tag matches the given query.'},
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


@mark.parametrize(
    'url,new_data,to_json,model',
    [
        [lf('note_list_url'), lf('new_note_data'), lf('note_to_json'), Note],
        [lf('tag_list_url'), lf('new_tag_data'), lf('tag_to_json'), Tag],
    ],
)
def test_create(
    author_client,
    url,
    new_data,
    to_json,
    model,
):
    obj_count = model.objects.count()

    response = author_client.post(url, data=new_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert model.objects.count() - obj_count == 1

    new_obj = model.objects.get(id=response.json()['id'])
    assert response.json() == to_json(new_obj)


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


@mark.parametrize(
    'url,new_data,model',
    [
        [lf('note_list_url'), lf('new_note_data'), Note],
        [lf('tag_list_url'), lf('new_tag_data'), Tag],
    ],
)
def test_prevent_create_duplicate(
    author_client,
    url,
    new_data,
    model,
):
    author_client.post(url, data=new_data)

    obj_count = model.objects.count()

    response = author_client.post(url, data=new_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert model.objects.count() == obj_count


@mark.parametrize('method', ['put', 'patch'])
@mark.parametrize(
    'client,status_code,to_json,expected_json,url,new_data,model,current_obj',
    [
        [
            lf('author_client'),
            status.HTTP_200_OK,
            lf('note_to_json'),
            lf('updated_note_json'),
            lf('note_detail_url'),
            lf('new_note_data'),
            Note,
            lf('some_note'),
        ],
        [
            lf('another_client'),
            status.HTTP_404_NOT_FOUND,
            lf('note_to_json'),
            lfc('note_to_json', lf('some_note')),
            lf('note_detail_url'),
            lf('new_note_data'),
            Note,
            lf('some_note'),
        ],
        [
            lf('author_client'),
            status.HTTP_200_OK,
            lf('tag_to_json'),
            lf('updated_tag_json'),
            lf('tag_detail_url'),
            lf('new_tag_data'),
            Tag,
            lf('some_tag'),
        ],
        [
            lf('another_client'),
            status.HTTP_404_NOT_FOUND,
            lf('tag_to_json'),
            lfc('tag_to_json', lf('some_tag')),
            lf('tag_detail_url'),
            lf('new_tag_data'),
            Tag,
            lf('some_tag'),
        ],
    ],
)
def test_update(
    client,
    status_code,
    to_json,
    expected_json,
    method,
    url,
    new_data,
    model,
    current_obj,
):
    request_func = getattr(client, method)
    response = request_func(url, data=new_data)
    assert response.status_code == status_code

    new_obj = model.objects.get(id=current_obj.id)
    assert to_json(new_obj) == expected_json
    assert current_obj.author == new_obj.author


@mark.parametrize(
    'client,status_code,deleted_items_count,url,model',
    [
        [
            lf('author_client'),
            status.HTTP_204_NO_CONTENT,
            1,
            lf('note_detail_url'),
            Note,
        ],
        [
            lf('another_client'),
            status.HTTP_404_NOT_FOUND,
            0,
            lf('note_detail_url'),
            Note,
        ],
        [
            lf('author_client'),
            status.HTTP_204_NO_CONTENT,
            1,
            lf('tag_detail_url'),
            Tag,
        ],
        [
            lf('another_client'),
            status.HTTP_404_NOT_FOUND,
            0,
            lf('tag_detail_url'),
            Tag,
        ],
    ],
)
def test_delete(
    client,
    status_code,
    deleted_items_count,
    url,
    model,
):
    obj_count = model.objects.count()

    response = client.delete(url)
    assert response.status_code == status_code

    assert obj_count - model.objects.count() == deleted_items_count


@mark.usefixtures('create_many_notes')
def test_notes_ordering(author_client, note_list_url):
    response = author_client.get(note_list_url)

    notes = response.json()
    assert notes == sorted(notes, key=lambda x: x['created_at'], reverse=True)


@mark.usefixtures('create_many_tags')
def test_tags_ordering(author_client, tag_list_url):
    response = author_client.get(tag_list_url)

    tags = response.json()
    assert tags == sorted(tags, key=lambda x: x['name'])


@mark.usefixtures('create_many_notes')
def test_note_title_filter(author_client, note_list_url):
    query = choice(choice(Note.objects.all()).title)

    response = author_client.get(note_list_url + f'?title={query}')
    response_ids = sorted(item['id'] for item in response.json())
    db_ids = sorted(
        note.id for note in Note.objects.filter(title__icontains=query)
    )

    assert response_ids == db_ids


@mark.usefixtures('create_many_notes')
def test_note_tags_filter(author_client, note_list_url):
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


@mark.usefixtures('create_many_tags')
def test_tag_name_filter(author_client, tag_list_url):
    query = choice(choice(Tag.objects.all()).name)

    response = author_client.get(tag_list_url + f'?name={query}')

    response_ids = sorted(item['id'] for item in response.json())
    db_ids = sorted(
        tag.id for tag in Tag.objects.filter(name__icontains=query)
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
        [lf('tag_list_url'), 'get'],
        [lf('tag_list_url'), 'post'],
        [lf('tag_detail_url'), 'get'],
        [lf('tag_detail_url'), 'put'],
        [lf('tag_detail_url'), 'patch'],
        [lf('tag_detail_url'), 'delete'],
    ],
)
def test_unauthorized_request(client, url, method):
    request_func = getattr(client, method)
    response = request_func(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
