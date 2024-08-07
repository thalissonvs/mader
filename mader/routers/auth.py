from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mader.database import get_session
from mader.models import User
from mader.schemas import TokenSchema
from mader.security import (
    create_access_token,
    get_current_user,
    verify_password,
)

router = APIRouter(prefix='/auth', tags=['auth'])
T_Session = Annotated[AsyncSession, Depends(get_session)]
T_Oauth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/token', response_model=TokenSchema)
async def login_for_access_token(form_data: T_Oauth2Form, session: T_Session):
    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=400, detail='Incorrect email or password'
        )

    access_token = create_access_token({'sub': user.email})
    return {'access_token': access_token, 'token_type': 'Bearer'}


@router.post('/refresh_token', response_model=TokenSchema)
def refresh_access_token(current_user: User = Depends(get_current_user)):
    access_token = create_access_token({'sub': current_user.email})
    return {'access_token': access_token, 'token_type': 'Bearer'}
