from pytest import mark
from pytest_lazy_fixtures import lf, lfc
from rest_framework import status

from diary.models import Tag

pytestmark = mark.django_db


@mark.usefixtures('some_tag')
@mark.parametrize(
    ['client', 'url', 'status_code', 'response_content'],
    [
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
    response_content,
):
    response = client.get(url)
    assert response.status_code == status_code
    assert response.json() == response_content


def test_create(
    author_client,
    tag_list_url,
    new_tag_data,
):
    tag_count = Tag.objects.count()

    response = author_client.post(tag_list_url, data=new_tag_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert Tag.objects.count() - tag_count == 1

    new_tag = Tag.objects.get(name=new_tag_data['name'])
    assert response.json() == {'id': new_tag.id, 'name': new_tag.name}


def test_prevent_create_duplicate(
    author_client,
    tag_list_url,
    new_tag_data,
):
    author_client.post(tag_list_url, data=new_tag_data)

    tag_count = Tag.objects.count()

    response = author_client.post(tag_list_url, data=new_tag_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Tag.objects.count() == tag_count


@mark.parametrize(
    ['client', 'status_code', 'expected_tag_name'],
    [
        [
            lf('author_client'),
            status.HTTP_200_OK,
            lfc(lambda x: x['name'], lf('new_tag_data')),
        ],
        [
            lf('another_client'),
            status.HTTP_404_NOT_FOUND,
            lfc(lambda x: x.name, lf('some_tag')),
        ],
    ],
)
def test_update(
    client,
    tag_detail_url,
    new_tag_data,
    status_code,
    some_tag,
    expected_tag_name,
):
    response = client.patch(tag_detail_url, data=new_tag_data)
    assert response.status_code == status_code

    new_tag = Tag.objects.get(id=some_tag.id)
    assert new_tag.name == expected_tag_name
    assert new_tag.author == some_tag.author


@mark.parametrize(
    ['client', 'status_code', 'deleted_items_count'],
    [
        [lf('author_client'), status.HTTP_204_NO_CONTENT, 1],
        [lf('another_client'), status.HTTP_404_NOT_FOUND, 0],
    ],
)
def test_delete(
    client,
    tag_detail_url,
    status_code,
    deleted_items_count,
):
    tag_count = Tag.objects.count()

    response = client.delete(tag_detail_url)
    assert response.status_code == status_code

    assert tag_count - Tag.objects.count() == deleted_items_count


@mark.usefixtures('create_many_tags')
def test_ordering(author_client, tag_list_url):
    response = author_client.get(tag_list_url)

    tags = response.json()
    print(tags)
    assert tags == sorted(tags, key=lambda x: x['name'])
