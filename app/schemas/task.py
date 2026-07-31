from datetime import datetime
from typing import Annotated, Literal, Optional
from pydantic import BaseModel, StringConstraints

Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Description = Annotated[str, StringConstraints(max_length=2000)]


class TaskCreate(BaseModel):
    title: Title
    description: Description = ""
    status: Literal["todo", "in_progress", "done"] = "todo"
    due_date: Optional[datetime] = None
    project_id: str
    assignee: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[Title] = None
    description: Optional[Description] = None
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
