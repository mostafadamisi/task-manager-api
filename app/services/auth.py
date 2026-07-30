from datetime import datetime, timezone
from fastapi import HTTPException, status
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.utils.security import hash_password, verify_password, create_access_token


async def register_user(data: UserCreate) -> UserResponse:
    db = get_db()
    existing = await db.users.find_one({"email": data.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = {
        "name": data.name,
        "email": data.email,
        "hashed_password": hash_password(data.password),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    result = await db.users.insert_one(user)

    return UserResponse(id=str(result.inserted_id), name=data.name, email=data.email)


async def login_user(data: UserLogin) -> TokenResponse:
    db = get_db()
    user = await db.users.find_one({"email": data.email})
    if not user or not verify_password(data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token({"sub": str(user["_id"])})
    return TokenResponse(access_token=token)
