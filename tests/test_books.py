from http import HTTPStatus

import pytest

from tests.conftest import BookFactory


def test_create_book(client, romancist, token):
    book = {
        'title': 'Pride and Prejudice',
        'year': '1813',
        'romancist_id': romancist.id,
    }
    response = client.post(
        '/books/',
        json=book,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'title': 'pride and prejudice',
        'year': '1813',
        'romancist_id': romancist.id,
    }


def test_create_book_unexistent_romancist(client, token):
    book = {
        'title': 'Pride and Prejudice',
        'year': '1813',
        'romancist_id': 1,
    }
    response = client.post(
        '/books/',
        json=book,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Romancist not found'}


def test_create_book_conflict(client, book, token):
    response = client.post(
        '/books/',
        json={
            'title': book.title,
            'year': '1813',
            'romancist_id': book.romancist_id,
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Book already exists in the MADR'}


def test_delete_book(client, book, token):
    response = client.delete(
        f'/books/{book.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Book deleted'}


def test_delete_book_not_found(client, token):
    response = client.delete(
        '/books/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Book not found'}


def test_read_book(client, book):
    response = client.get(f'/books/{book.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': book.id,
        'title': 'pride and prejudice',
        'year': '1813',
        'romancist_id': book.romancist_id,
    }


def test_read_book_not_found(client):
    response = client.get('/books/1')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Book not found'}


def test_read_books_with_book(client, book):
    response = client.get('/books/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'books': [
            {
                'id': book.id,
                'title': 'pride and prejudice',
                'year': '1813',
                'romancist_id': book.romancist_id,
            }
        ]
    }


def test_read_books_with_no_books(client):
    response = client.get('/books/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'books': []}


@pytest.mark.asyncio
async def test_read_books_with_title(client, session):
    session.add_all(BookFactory.build_batch(5))
    await session.commit()

    response = client.get('/books/?title=0')

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['books']) == 1
    assert response.json() == {
        'books': [{'id': 1, 'title': 'book0', 'year': '0', 'romancist_id': 1}]
    }


@pytest.mark.asyncio
async def test_read_books_with_year(client, session):
    expected_books = 5
    session.add_all(BookFactory.build_batch(5, year='1900'))
    await session.commit()

    response = client.get('/books/?year=1900')

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['books']) == expected_books


@pytest.mark.asyncio
async def test_read_books_with_title_and_year(client, session):
    expected_books = 1
    session.add_all(BookFactory.build_batch(5, year='1900'))
    await session.commit()

    response = client.get('/books/?title=book10&year=1900')

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['books']) == expected_books


@pytest.mark.asyncio
async def test_read_books_with_title_and_year_should_return_0(client, session):
    expected_books = 0
    session.add_all(BookFactory.build_batch(5, year='1900'))
    await session.commit()

    response = client.get('/books/?title=book10&year=1901')

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['books']) == expected_books


@pytest.mark.asyncio
async def test_read_books_with_limit(client, session):
    expected_books = 20
    session.add_all(BookFactory.build_batch(25))
    await session.commit()

    response = client.get('/books/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['books']) == expected_books


@pytest.mark.asyncio
async def test_read_books_with_limit_and_offset(client, session):
    expected_books = 5
    session.add_all(BookFactory.build_batch(25))
    await session.commit()

    response = client.get('/books/?offset=20')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['books']) == expected_books


@pytest.mark.asyncio
async def test_read_books_with_limit_and_offset_and_title(client, session):
    expected_books = 15
    session.add_all(BookFactory.build_batch(25))
    await session.commit()

    response = client.get('/books/?title=book&offset=10')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['books']) == expected_books


def test_update_book(client, book, token):
    response = client.patch(
        f'/books/{book.id}',
        json={'title': 'new title'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': book.id,
        'title': 'new title',
        'year': book.year,
        'romancist_id': book.romancist_id,
    }


def test_update_book_not_found(client, token):
    response = client.patch(
        '/books/1',
        json={'title': 'new title'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Book not found'}


def test_update_book_romancist_not_found(
    client, book_invalid_romancist, token
):
    response = client.patch(
        f'/books/{book_invalid_romancist.id}',
        json={'romancist_id': book_invalid_romancist.romancist_id},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Romancist not found'}


def test_update_book_with_no_data(client, book, token):
    response = client.patch(
        f'/books/{book.id}',
        json={},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': book.id,
        'title': book.title,
        'year': book.year,
        'romancist_id': book.romancist_id,
    }
