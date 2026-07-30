from fastapi import APIRouter, Request, status
from app.dependencies import limiter
from app.schemas.user import UserCreate, UserLogin, TokenResponse
from app.services.auth import register_user, login_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def register(request: Request, data: UserCreate):
    return await register_user(data)


@router.post("/login")
@limiter.limit("30/minute")
async def login(request: Request, data: UserLogin) -> TokenResponse:
    return await login_user(data)
