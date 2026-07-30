from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class TaskCreate(BaseModel):
    title: str
    description: str
    status: str = "todo"
    due_date: Optional[datetime] = None
    project_id: str
    assignee: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None
    assignee: Optional[str] = None


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    status: str
    due_date: Optional[datetime]
    project_id: str
    assignee: Optional[str]
    created_by: str
    created_at: datetime

