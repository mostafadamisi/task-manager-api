from datetime import datetime, timezone
from pydantic import BaseModel
from typing import Optional


class Activity(BaseModel):
    task_id: str
    user_id: str
    action: str
    changes: Optional[dict] = None
    timestamp: datetime = datetime.now(timezone.utc)
