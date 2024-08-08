from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from mader.common import T_CurrentUser, T_Session
from mader.models import Book, Romancist
from mader.schemas import (
    BookPublic,
    BookSchema,
    BooksList,
    BookUpdate,
    Message,
)
from mader.utils import sanitize_username

router = APIRouter(prefix='/books', tags=['books'])


@router.post('/', status_code=HTTPStatus.CREATED, response_model=BookPublic)
async def create_book(
    book: BookSchema, session: T_Session, current_user: T_CurrentUser
):
    sanitized_title = sanitize_username(book.title)

    db_book = await session.scalar(
        select(Book)
        .where(Book.title == sanitized_title)
        .options(selectinload(Book.romancist))
    )

    db_romancist = await session.scalar(
        select(Romancist).where(Romancist.id == book.romancist_id)
    )

    if db_book:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Book already exists in the MADR',
        )

    if not db_romancist:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Romancist not found',
        )

    db_book = Book(
        title=sanitized_title, year=book.year, romancist_id=book.romancist_id
    )
    session.add(db_book)
    await session.commit()
    await session.refresh(db_book)

    return db_book


@router.delete('/{book_id}', response_model=Message)
async def delete_book(
    book_id: int, session: T_Session, current_user: T_CurrentUser
):
    db_book = await session.scalar(select(Book).where(Book.id == book_id))

    if not db_book:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Book not found',
        )

    await session.delete(db_book)
    await session.commit()

    return {'message': 'Book deleted'}


@router.get('/{book_id}', response_model=BookPublic)
async def read_book(session: T_Session, book_id: int):
    db_book = await session.scalar(select(Book).where(Book.id == book_id))

    if not db_book:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Book not found',
        )

    return db_book


@router.get('/', response_model=BooksList)
async def read_books(
    session: T_Session,
    title: str | None = None,
    year: str | None = None,
    limit: int = 20,
    offset: int = 0,
):
    query = select(Book)

    if title:
        query = query.filter(Book.title.contains(title))

    if year:
        query = query.filter(Book.year == year)

    books = await session.scalars(query.offset(offset).limit(limit))
    return {'books': books}


@router.patch('/{book_id}', response_model=BookPublic)
async def update_book(
    session: T_Session,
    book_id: int,
    book: BookUpdate,
    current_user: T_CurrentUser,
):
    db_book = await session.scalar(select(Book).where(Book.id == book_id))
    if not db_book:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Book not found',
        )

    db_romancist = await session.scalar(
        select(Romancist).where(Romancist.id == db_book.romancist_id)
    )

    if not db_romancist:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Romancist not found',
        )

    for key, value in book.model_dump(exclude_unset=True).items():
        setattr(db_book, key, value)

    await session.commit()
    await session.refresh(db_book)

    return db_book
