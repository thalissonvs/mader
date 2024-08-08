from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from mader.common import T_CurrentUser, T_Session
from mader.models import User
from mader.schemas import UserPublic, UserSchema, UsersList
from mader.security import get_password_hash
from mader.utils import sanitize_username

router = APIRouter(prefix='/users', tags=['users'])


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(user: UserSchema, session: T_Session):
    db_user = await session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='User already exists in the MADR',
        )

    sanitized_username = sanitize_username(user.username)

    db_user = User(
        username=sanitized_username,
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
async def delete_user(
    user_id: int, session: T_Session, current_user: T_CurrentUser
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Unauthorized',
        )

    await session.delete(current_user)
    await session.commit()
    return {'message': 'User deleted'}


@router.put('/{user_id}', response_model=UserPublic)
async def update_user(
    user_id: int,
    user: UserSchema,
    session: T_Session,
    current_user: T_CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Unauthorized',
        )

    sanitized_username = sanitize_username(user.username)

    current_user.username = sanitized_username
    current_user.email = user.email
    current_user.password = get_password_hash(user.password)
    await session.commit()
    await session.refresh(current_user)

    return current_user
