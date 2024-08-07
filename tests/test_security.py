from http import HTTPStatus

from mader.security import create_access_token


def test_valid_token_with_unexistent_user(client, user):
    token = create_access_token({'sub': 'user_not_in_db@mail.com'})
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Unauthorized'}


def test_invalid_token(client, user):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': 'Bearer invalid_token'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Unauthorized'}


def test_no_sub_token(client, user):
    token = create_access_token({})
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Unauthorized'}
