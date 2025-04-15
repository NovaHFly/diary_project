from django.contrib.auth import get_user_model
from pytest import mark
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
    client,
    users_list_url,
    user_to_json,
):
    response = client.post(users_list_url, data=new_user_data)
    assert response.status_code == status.HTTP_201_CREATED

    new_user = User.objects.get(username=new_user_data['username'])
    new_user_data['id'] = new_user.id

    new_user_data.pop('password')

    assert response.json() == new_user_data == user_to_json(new_user)


def test_prevent_create_duplicate_user(
    client,
    users_list_url,
):
    client.post(users_list_url, data=new_user_data)

    user_count = User.objects.count()

    response = client.post(users_list_url, data=new_user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert User.objects.count() == user_count


def test_login_user(client, some_user, token_login_url, user_password):
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
    token_login_url,
    token_logout_url,
    user_password,
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
    some_user_client,
    user_to_json,
    user_profile_url,
):
    response = some_user_client.get(user_profile_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == user_to_json(some_user_client.user)


def test_update_self_profile(
    some_user_client,
    user_to_json,
    user_profile_url,
):
    new_data = {'email': 'another_email@mail.ru'}

    response = some_user_client.put(user_profile_url, data=new_data)
    assert response.status_code == status.HTTP_200_OK

    new_user = User.objects.get(id=some_user_client.user.id)
    user_json = user_to_json(new_user)

    new_data = user_json | new_data

    assert response.json() == user_json == new_data


def test_invalid_update_profile(
    some_user_client,
    user_to_json,
    user_profile_url,
):
    new_data = {'email': 'not_an_email'}

    response = some_user_client.put(user_profile_url, data=new_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    new_user = User.objects.get(id=some_user_client.user.id)
    assert user_to_json(new_user) == user_to_json(some_user_client.user)


def test_delete_self_profile(
    some_user_client,
    user_profile_url,
    user_password,
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
    user_set_username_url,
    user_password,
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
    user_set_password_url,
    token_login_url,
    user_password,
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
