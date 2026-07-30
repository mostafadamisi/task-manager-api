from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    description: str
    status: Literal["todo", "in_progress", "done"] = "todo"
    due_date: Optional[datetime] = None
    project_id: str
    assignee: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[Literal["todo", "in_progress", "done"]] = None
    due_date: Optional[datetime] = None
    assignee: Optional[str] = None


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    status: Literal["todo", "in_progress", "done"]
    due_date: Optional[datetime]
    project_id: str
    assignee: Optional[str]
    created_by: str
    created_at: datetime

