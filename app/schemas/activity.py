from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ActivityResponse(BaseModel):
    id: str
    task_id: str
    user_id: str
    action: str
    changes: Optional[dict]
    timestamp: datetime

    class Config:
        from_attributes = True
