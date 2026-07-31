from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, Field, StringConstraints

ProjectName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]


class ProjectCreate(BaseModel):
    name: ProjectName
    description: Annotated[str, StringConstraints(max_length=2000)] = ""
    members: list[str] = Field(default_factory=list, max_length=50)


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    owner: str
    members: list[str]
    created_at: datetime
