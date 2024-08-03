from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from mader.database import get_session
from mader.schemas import UsersList

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/', response_model=UsersList)
async def read_users(session: Session = Depends(get_session)):
    return {'users': []}
