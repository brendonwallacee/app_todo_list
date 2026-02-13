from http import HTTPStatus

import pytest

from api_acess_alterdata.schemas import UserPublic


def test_root_return_ola_mundo(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá mundo!'}


def test_return_ola_mundo_html(client):
    response = client.get('/html')

    assert response.status_code == HTTPStatus.OK
    assert (
        response.text
        == """
    <html>
      <body>
        <h1>Olá mundo!</h1>
      </body>
    </html>
    """
    )


def test_create_user(client):
    user_data = {
        'username': 'alice',
        'email': 'alice@example.com',
        'password': 'secret',
    }

    response = client.post('/users/', json=user_data)

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'alice',
        'email': 'alice@example.com',
        'id': 1,
    }


def test_create_user_conflict_username(client, user):

    user_data = {
        'username': user.username,
        'email': 'alice@example.com',
        'password': 'secret',
    }

    response = client.post('/users/', json=user_data)

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username já existe'}


def test_create_user_conflict_email(client, user):

    user_data = {
        'username': 'alice',
        'email': user.email,
        'password': 'secret',
    }

    response = client.post('/users/', json=user_data)

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email já existe'}


def test_read_users(client, user, token):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get(
        '/users/', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user, token):
    updated_user_data = {
        'username': 'bob',
        'email': 'bob@example.com',
        'password': 'secret',
    }

    response = client.put(
        f'/users/{user.id}',
        json=updated_user_data,
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'bob',
        'email': 'bob@example.com',
        'id': 1,
    }


def test_update_user_unauthorized(client, token):
    updated_user_data = {
        'username': 'bob',
        'email': 'bob@example.com',
        'password': 'secret',
    }

    response = client.put(
        '/users/2',
        json=updated_user_data,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'Permissão insuficiente',
    }


def test_update_integrity_error(client, user, token):
    # Cria um segundo usuário para causar um conflito de email
    second_user_data = {
        'username': 'charlie',
        'email': 'charlie@example.com',
        'password': 'secret',
    }

    client.post('/users/', json=second_user_data)

    updated_user_data = {
        'username': 'bob',
        'email': 'charlie@example.com',
        'password': 'secret',
    }

    response = client.put(
        f'/users/{user.id}',
        json=updated_user_data,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username ou email ja cadastrado'}


def test_read_user(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


@pytest.mark.parametrize('user_id', [2, 0, -1])
def test_read_user_not_found(client, user_id):
    response = client.get(f'/users/{user_id}')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        'detail': 'Usuário não encontrado',
    }


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'message': 'Usuário deletado com sucesso',
    }


def test_delete_user_unauthorized(client, token):

    response = client.delete(
        '/users/2', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'Não autorizado a deletar este usuário',
    }


def test_get_token(client, user):
    login = {
        'username': user.email,
        'password': user.clean_password,
    }
    response = client.post('/token', data=login)

    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token


def test_get_token_invalid_credentials(client):
    login = {
        'username': 'test',
        'password': 'test',
    }
    response = client.post('/token', data=login)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Usuário ou senha incorretos'}


def test_get_token_invalid_password(client, user):
    login = {
        'username': user.email,
        'password': 'invalid',
    }
    response = client.post('/token', data=login)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Usuário ou senha incorretos'}
