from http import HTTPStatus

import pytest

from tests.conftest import RomancistFactory


def test_create_romancist(client, token):
    romancist = {'name': 'Jane Austen'}
    response = client.post(
        '/romancists/',
        json=romancist,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {'id': 1, 'name': 'jane austen'}


def test_create_romancist_unauthorized(client):
    romancist = {'name': 'Jane Austen'}
    response = client.post('/romancists/', json=romancist)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


def test_create_romancist_conflict(client, romancist, token):
    response = client.post(
        '/romancists/',
        json={'name': romancist.name},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'Romancist already exists in the MADR'
    }


def test_read_romancist(client, romancist):
    response = client.get(f'/romancists/{romancist.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'id': 1, 'name': 'jane austen'}


def test_read_romancist_not_found(client):
    response = client.get('/romancists/1')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Romancist not found'}


def test_read_romancists_with_romancist(client, romancist):
    response = client.get('/romancists/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'romancists': [{'id': 1, 'name': 'jane austen'}]
    }


def test_read_romancists_with_no_romancists(client):
    response = client.get('/romancists/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'romancists': []}


@pytest.mark.asyncio
async def test_read_romancists_with_name(client, session):
    session.add_all(RomancistFactory.build_batch(5))
    await session.commit()

    response = client.get('/romancists/?name=1')

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['romancists']) == 1
    assert response.json()['romancists'][0]['name'] == 'romancist1'


@pytest.mark.asyncio
async def test_read_romancists_with_name_should_return_5(client, session):
    expected_romancists = 5
    session.add_all(RomancistFactory.build_batch(5))
    await session.commit()

    response = client.get('/romancists/?name=romancist')

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['romancists']) == expected_romancists


@pytest.mark.asyncio
async def test_read_romancists_with_name_should_return_0(client, session):
    expected_romancists = 0
    session.add_all(RomancistFactory.build_batch(5))
    await session.commit()

    response = client.get('/romancists/?name=test')

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['romancists']) == expected_romancists


def test_delete_romancist(client, romancist, token):
    response = client.delete(
        f'/romancists/{romancist.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Romancist deleted from the MADR'}


def test_delete_romancist_not_found(client, token):
    response = client.delete(
        '/romancists/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Romancist not found'}


def test_delete_romancist_unauthorized(client, romancist):
    response = client.delete(f'/romancists/{romancist.id}')

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


def test_update_romancist(client, romancist, token):
    updated_romancist = {'name': 'Clarice Lispector'}
    response = client.patch(
        f'/romancists/{romancist.id}',
        json=updated_romancist,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'id': 1, 'name': 'clarice lispector'}


def test_update_romancist_not_found(client, token):
    updated_romancist = {'name': 'Clarice Lispector'}
    response = client.patch(
        '/romancists/1',
        json=updated_romancist,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Romancist not found'}


def test_update_romancist_unauthorized(client, romancist):
    updated_romancist = {'name': 'Clarice Lispector'}
    response = client.patch(
        f'/romancists/{romancist.id}',
        json=updated_romancist,
        headers={'Authorization': 'Bearer invalid-token'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Unauthorized'}
