from datetime import datetime, timezone
from pydantic import BaseModel
from typing import Optional


class Task(BaseModel):
    title: str
    description: str
    status: str = "todo"
    due_date: Optional[datetime] = None
    project_id: str
    assignee: Optional[str] = None
    created_by: str
    created_at: datetime = datetime.now(timezone.utc)
