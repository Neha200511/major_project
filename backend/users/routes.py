from fastapi import APIRouter, Depends, HTTPException
from backend.auth.security import get_current_user
from backend.users.service import get_user_contacts, get_user_profile
from backend.utils.helpers import format_user
from backend.database.mongodb import get_database

router = APIRouter(prefix='/api/users', tags=['Users'])

@router.get('/profile')
async def get_profile(current_user: dict = Depends(get_current_user)):
    return {'user': current_user}

@router.get('/contacts')
async def get_contacts(current_user: dict = Depends(get_current_user)):
    contacts = get_user_contacts(current_user['_id'], current_user['role'])
    return {'contacts': contacts}

@router.get('/{user_id}')
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    profile = get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail='User not found')
    return {'user': {'_id': profile['_id'], 'name': profile['name'], 'role': profile['role'], 'status': profile['status'], 'last_active': profile['last_active']}}
