from fastapi import APIRouter

from mader.schemas import UsersList

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/', response_model=UsersList)
async def read_users():
    return {
        'users': []
    }
