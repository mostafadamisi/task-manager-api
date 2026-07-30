from datetime import datetime, timezone
from typing import Literal, Optional
from pydantic import BaseModel


class Task(BaseModel):
    title: str
    description: str
    status: Literal["todo", "in_progress", "done"] = "todo"
    due_date: Optional[datetime] = None
    project_id: str
    assignee: Optional[str] = None
    created_by: str
    created_at: datetime = datetime.now(timezone.utc)
