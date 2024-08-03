from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from mader.database import get_session
from mader.models import User
from mader.schemas import UserPublic, UserSchema, UsersList

router = APIRouter(prefix='/users', tags=['users'])
T_Session = Annotated[Session, Depends(get_session)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(user: UserSchema, session: T_Session):
    db_user = await session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='User with this username or email already exists',
        )

    db_user = User(
        username=user.username, email=user.email, password=user.password
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.get('/', response_model=UsersList)
async def read_users(session: T_Session, limit: int = 100, offset: int = 0):
    users = await session.scalars(select(User).limit(limit).offset(offset))
    return {'users': users}
