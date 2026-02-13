from http import HTTPStatus


def test_get_token(client, user):
    login = {
        'username': user.email,
        'password': user.clean_password,
    }
    response = client.post('/auth/token', data=login)

    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token


def test_get_token_invalid_credentials(client):
    login = {
        'username': 'test',
        'password': 'test',
    }
    response = client.post('/auth/token', data=login)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Usuário ou senha incorretos'}


def test_get_token_invalid_password(client, user):
    login = {
        'username': user.email,
        'password': 'invalid',
    }
    response = client.post('/auth/token', data=login)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Usuário ou senha incorretos'}
