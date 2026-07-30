from datetime import datetime, timezone
from pydantic import BaseModel


class User(BaseModel):
    name: str
    email: str
    hashed_password: str
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)
