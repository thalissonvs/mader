from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from mader.common import T_CurrentUser, T_Session
from mader.models import Romancist
from mader.schemas import (
    Message,
    RomancistPublic,
    RomancistSchema,
    RomancistsList,
    RomancistUpdate,
)
from mader.utils import sanitize_username

router = APIRouter(prefix='/romancists', tags=['romancists'])


@router.post(
    '/', response_model=RomancistPublic, status_code=HTTPStatus.CREATED
)
async def create_romancist(
    romancist: RomancistSchema, session: T_Session, current_user: T_CurrentUser
):
    name = sanitize_username(romancist.name)
    db_romancist = await session.scalar(
        select(Romancist).where(Romancist.name == name)
    )

    if db_romancist:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Romancist already exists in the MADR',
        )

    db_romancist = Romancist(name=name)
    session.add(db_romancist)
    await session.commit()
    await session.refresh(db_romancist)

    return db_romancist


@router.get('/{romancist_id}', response_model=RomancistPublic)
async def read_romancist(session: T_Session, romancist_id: int):
    romancist = await session.scalar(
        select(Romancist).where(Romancist.id == romancist_id)
    )
    if not romancist:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Romancist not found',
        )

    return romancist


@router.get('/', response_model=RomancistsList)
async def read_romancists(session: T_Session, name: str | None = None):
    query = select(Romancist)

    if name:
        query = query.filter(Romancist.name.contains(name))

    romancists = await session.scalars(query)
    return {'romancists': romancists}


@router.delete('/{romancist_id}', response_model=Message)
async def delete_romancist(
    romancist_id: int, session: T_Session, current_user: T_CurrentUser
):
    romancist = await session.scalar(
        select(Romancist).where(Romancist.id == romancist_id)
    )
    if not romancist:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Romancist not found',
        )

    await session.delete(romancist)
    await session.commit()
    return {'message': 'Romancist deleted from the MADR'}


@router.patch('/{romancist_id}', response_model=RomancistPublic)
async def update_romancist(
    romancist_id: int,
    romancist: RomancistUpdate,
    session: T_Session,
    current_user: T_CurrentUser,
):
    db_romancist = await session.scalar(
        select(Romancist).where(Romancist.id == romancist_id)
    )
    if not db_romancist:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Romancist not found',
        )

    if romancist.name:
        db_romancist.name = sanitize_username(romancist.name)

    await session.commit()
    await session.refresh(db_romancist)

    return db_romancist
