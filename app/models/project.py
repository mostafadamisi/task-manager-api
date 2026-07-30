from datetime import datetime, timezone
from pydantic import BaseModel


class Project(BaseModel):
    name: str
    description: str
    owner: str
    members: list[str]
    created_at: datetime = datetime.now(timezone.utc)
