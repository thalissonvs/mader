from http import HTTPStatus

import freezegun


def test_auth(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json().get('access_token')
    assert response.json().get('token_type') == 'Bearer'


def test_auth_with_incorrect_password(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': 'incorrect_password'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json().get('detail') == 'Incorrect email or password'


def test_auth_with_incorrect_email(client, user):
    response = client.post(
        '/auth/token',
        data={'username': 'invalid_email', 'password': user.clean_password},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json().get('detail') == 'Incorrect email or password'


def test_refresh_token(client, token):
    response = client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['access_token']
    assert response.json()['token_type'] == 'Bearer'


def test_refresh_token_expired_token(client, user):
    with freezegun.freeze_time('2022-01-01 00:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freezegun.freeze_time('2022-01-01 00:31:00'):
        response = client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json()['detail'] == 'Unauthorized'
