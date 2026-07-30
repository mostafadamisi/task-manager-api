from fastapi import APIRouter, status
from app.schemas.user import UserCreate, UserLogin, TokenResponse
from app.services.auth import register_user, login_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate):
    return await register_user(data)


@router.post("/login")
async def login(data: UserLogin) -> TokenResponse:
    return await login_user(data)
