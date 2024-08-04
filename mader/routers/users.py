from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mader.database import get_session
from mader.models import User
from mader.schemas import UserPublic, UserSchema, UsersList
from mader.security import get_password_hash

router = APIRouter(prefix='/users', tags=['users'])
T_Session = Annotated[AsyncSession, Depends(get_session)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(user: UserSchema, session: T_Session):
    db_user = await session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='User with this username already exists',
            )

        if db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='User with this email already exists',
            )

    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.get('/', response_model=UsersList)
async def read_users(session: T_Session, limit: int = 100, offset: int = 0):
    users = await session.scalars(select(User).limit(limit).offset(offset))
    return {'users': users}


@router.delete('/{user_id}')
async def delete_user(user_id: int, session: T_Session):
    db_user = await session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found',
        )

    session.delete(db_user)
    await session.commit()
    return {'message': 'User deleted'}


@router.put('/{user_id}', response_model=UserPublic)
async def update_user(user_id: int, user: UserSchema, session: T_Session):
    db_user = await session.scalar(select(User).where(User.id == user_id))
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found',
        )

    db_user.username = user.username
    db_user.email = user.email
    db_user.password = get_password_hash(user.password)
    await session.commit()
    await session.refresh(db_user)

    return db_user
