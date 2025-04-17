from django.contrib.auth import get_user_model
from pytest import mark
from pytest_lazy_fixtures import lf
from rest_framework import status
from rest_framework.authtoken.models import Token

User = get_user_model()

pytestmark = mark.django_db


new_user_data = {
    'username': 'new_user',
    'email': 'new_user@mail.com',
    'password': 'S0m3P@55w0rd',
}


def test_create_user(
    user_to_json,
    client,
    user_list_url,
):
    response = client.post(user_list_url, data=new_user_data)
    assert response.status_code == status.HTTP_201_CREATED

    new_user = User.objects.get(username=new_user_data['username'])
    new_user_data['id'] = new_user.id

    new_user_data.pop('password')

    assert response.json() == new_user_data == user_to_json(new_user)


def test_prevent_create_duplicate_user(
    client,
    user_list_url,
):
    client.post(user_list_url, data=new_user_data)

    user_count = User.objects.count()

    response = client.post(user_list_url, data=new_user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert User.objects.count() == user_count


def test_login_user(
    client,
    some_user,
    user_password,
    token_login_url,
):
    token_count = Token.objects.count()

    response = client.post(
        token_login_url,
        data={
            'username': some_user.username,
            'password': user_password,
        },
    )
    assert response.status_code == status.HTTP_200_OK

    assert Token.objects.count() - token_count == 1
    new_token = Token.objects.get(user=some_user)

    assert response.json() == {'auth_token': new_token.key}


def test_logout_user(
    client,
    some_user,
    user_password,
    token_login_url,
    token_logout_url,
):
    client.post(
        token_login_url,
        data={
            'username': some_user.username,
            'password': user_password,
        },
    )

    token_count = Token.objects.count()
    token_value = Token.objects.get(user=some_user).key

    response = client.post(
        token_logout_url,
        headers={'Authorization': f'Token {token_value}'},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert token_count - Token.objects.count() == 1


def test_get_self_profile(
    user_to_json,
    some_user_client,
    user_profile_url,
):
    response = some_user_client.get(user_profile_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == user_to_json(some_user_client.user)


@mark.parametrize('method', ['put', 'patch'])
def test_update_self_profile(
    user_to_json,
    some_user_client,
    user_profile_url,
    method,
):
    new_data = {'email': 'another_email@mail.ru'}

    request_func = getattr(some_user_client, method)
    response = request_func(user_profile_url, data=new_data)
    assert response.status_code == status.HTTP_200_OK

    new_user = User.objects.get(id=some_user_client.user.id)
    user_json = user_to_json(new_user)

    new_data = user_json | new_data

    assert response.json() == user_json == new_data


def test_invalid_update_profile(
    user_to_json,
    some_user_client,
    user_profile_url,
):
    new_data = {'email': 'not_an_email'}

    response = some_user_client.put(user_profile_url, data=new_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    new_user = User.objects.get(id=some_user_client.user.id)
    assert user_to_json(new_user) == user_to_json(some_user_client.user)


def test_delete_self_profile(
    some_user_client,
    user_password,
    user_profile_url,
):
    user_count = User.objects.count()

    response = some_user_client.delete(
        user_profile_url,
        data={'current_password': user_password},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert user_count - User.objects.count() == 1


def test_set_username(
    some_user_client,
    user_password,
    user_set_username_url,
):
    new_username = 'somebody_else'

    response = some_user_client.post(
        user_set_username_url,
        data={
            'new_username': new_username,
            'current_password': user_password,
        },
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    new_user = User.objects.get(id=some_user_client.user.id)
    assert new_user.username == new_username


def test_set_password(
    some_user_client,
    user_password,
    user_set_password_url,
    token_login_url,
):
    new_password = 'S3cr37P@55w0r6'

    response = some_user_client.post(
        user_set_password_url,
        data={
            'new_password': new_password,
            'current_password': user_password,
        },
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    auth_response = some_user_client.post(
        token_login_url,
        data={
            'username': some_user_client.user.username,
            'password': new_password,
        },
    )
    assert auth_response.status_code == status.HTTP_200_OK


@mark.parametrize(
    'url,method',
    [
        [lf('user_list_url'), 'get'],
        [lf('user_detail_url'), 'get'],
        [lf('user_detail_url'), 'put'],
        [lf('user_detail_url'), 'patch'],
        [lf('user_detail_url'), 'delete'],
        [lf('user_profile_url'), 'get'],
        [lf('user_profile_url'), 'put'],
        [lf('user_profile_url'), 'patch'],
        [lf('user_profile_url'), 'delete'],
        [lf('user_set_username_url'), 'post'],
        [lf('user_set_password_url'), 'post'],
        [lf('token_logout_url'), 'post'],
    ],
)
def test_unauthorized_request(
    client,
    url,
    method,
):
    request_func = getattr(client, method)
    response = request_func(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@mark.usefixtures('another_user')
def test_cannot_see_other_users(
    user_to_json,
    some_user_client,
    user_list_url,
):
    response = some_user_client.get(user_list_url)
    assert response.json() == [user_to_json(some_user_client.user)]


def test_cannot_see_other_user_profile(
    some_user_client,
    user_detail_url,
):
    response = some_user_client.get(user_detail_url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@mark.parametrize('method', ['put', 'patch'])
def test_cannot_update_other_user_profile(
    user_to_json,
    some_user_client,
    another_user,
    user_detail_url,
    method,
):
    user_data = user_to_json(another_user)

    request_func = getattr(some_user_client, method)
    response = request_func(
        user_detail_url,
        data={'email': 'new_email@mail.com'},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

    new_user = User.objects.get(id=user_data['id'])
    assert user_to_json(new_user) == user_data


@mark.xfail(reason=('Djoser does not hide that user exists while deleting'))
def test_cannot_delete_other_user_profile(
    some_user_client,
    user_detail_url,
):
    user_count = User.objects.count()

    response = some_user_client.delete(user_detail_url)
    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert user_count - User.objects.count() == 0
