from datetime import datetime
from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    description: str
    members: list[str] = []


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    owner: str
    members: list[str]
    created_at: datetime

    class Config:
        from_attributes = True
