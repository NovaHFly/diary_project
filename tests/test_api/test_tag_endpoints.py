from pytest import mark
from pytest_lazy_fixtures import lf, lfc
from rest_framework import status

from diary.models import Tag

pytestmark = mark.django_db


@mark.usefixtures('some_tag')
@mark.parametrize(
    ['client', 'response_content'],
    [
        [
            lf('author_client'),
            [lfc(lambda x: {'id': x.id, 'name': x.name}, lf('some_tag'))],
        ],
        [lf('another_client'), []],
    ],
)
def test_get_list(
    client,
    tag_list_url,
    response_content,
):
    response = client.get(tag_list_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_content


@mark.usefixtures('some_note')
@mark.parametrize(
    ['client', 'status_code', 'response_content'],
    [
        [
            lf('author_client'),
            status.HTTP_200_OK,
            lfc(
                lambda x: {
                    'id': x.id,
                    'name': x.name,
                },
                lf('some_tag'),
            ),
        ],
        [lf('another_client'), status.HTTP_404_NOT_FOUND, None],
    ],
)
def test_get_detail(
    client,
    tag_detail_url,
    status_code,
    response_content,
):
    response = client.get(tag_detail_url)
    assert response.status_code == status_code
    if response.status_code == status.HTTP_200_OK:
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


def test_update_own(
    author_client,
    some_tag,
    tag_detail_url,
    new_tag_data,
):
    response = author_client.patch(tag_detail_url, data=new_tag_data)
    assert response.status_code == status.HTTP_200_OK

    new_tag = Tag.objects.get(id=some_tag.id)
    assert new_tag.name == new_tag_data['name']
    assert new_tag.author == some_tag.author


def test_update_different_user(
    another_client,
    some_tag,
    tag_detail_url,
    new_tag_data,
):
    response = another_client.patch(tag_detail_url, data=new_tag_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND

    new_tag = Tag.objects.get(id=some_tag.id)
    assert new_tag.name == some_tag.name
    assert new_tag.author == some_tag.author


def test_delete_own(
    author_client,
    tag_detail_url,
):
    tag_count = Tag.objects.count()

    response = author_client.delete(tag_detail_url)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert tag_count - Tag.objects.count() == 1


def test_delete_different_user(
    another_client,
    tag_detail_url,
):
    tag_count = Tag.objects.count()

    response = another_client.delete(tag_detail_url)
    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert tag_count - Tag.objects.count() == 0


@mark.usefixtures('create_many_tags')
def test_ordering(author_client, tag_list_url):
    response = author_client.get(tag_list_url)

    tags = response.json()
    print(tags)
    assert tags == sorted(tags, key=lambda x: x['name'])
