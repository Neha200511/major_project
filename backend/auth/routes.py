from fastapi import APIRouter, HTTPException, status, Request, Depends
from backend.database.models import UserCreate, UserLogin
from backend.auth.service import register_user, authenticate_user, create_audit_log, update_user_status
from backend.auth.security import create_access_token, get_current_user, check_rate_limit

router = APIRouter(prefix='/api/auth', tags=['Authentication'])

@router.post('/register')
async def register(user_data: UserCreate):
    user = register_user(user_data.name, user_data.email, user_data.password, user_data.role.value)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already registered')
    token = create_access_token({'sub': user['_id'], 'role': user['role']})
    create_audit_log(user['_id'], 'REGISTER', f'New {user["role"]} account created')
    return {'token': token, 'user': user}

@router.post('/login')
async def login(credentials: UserLogin, request: Request):
    client_ip = request.client.host if request.client else 'unknown'
    if not check_rate_limit(client_ip):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail='Too many login attempts. Please try again later.')
    user = authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email or password')
    token = create_access_token({'sub': user['_id'], 'role': user['role']})
    update_user_status(user['_id'], 'online')
    create_audit_log(user['_id'], 'LOGIN', 'User logged in')
    return {'token': token, 'user': user}

@router.post('/logout')
async def logout(current_user: dict = Depends(get_current_user)):
    update_user_status(current_user['_id'], 'offline')
    create_audit_log(current_user['_id'], 'LOGOUT', 'User logged out')
    return {'message': 'Logged out successfully'}

@router.get('/me')
async def get_me(current_user: dict = Depends(get_current_user)):
    return {'user': current_user}
