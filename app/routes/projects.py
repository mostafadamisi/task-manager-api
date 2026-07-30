from typing import Optional
from fastapi import APIRouter, Depends, Query, Request, status
from app.dependencies import get_current_user_id, limiter
from app.schemas.project import ProjectCreate, ProjectResponse
from app.services.project import create_project, get_all_projects, get_project_by_id, delete_project

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", status_code=status.HTTP_201_CREATED)
@limiter.limit("120/minute")
async def create(request: Request, data: ProjectCreate, user_id: str = Depends(get_current_user_id)):
    return await create_project(data, user_id)


@router.get("/")
@limiter.limit("120/minute")
async def list_all(
    request: Request,
    page: Optional[int] = Query(1, ge=1),
    limit: Optional[int] = Query(20, ge=1, le=100),
):
    return await get_all_projects(page, limit)


@router.get("/{project_id}")
@limiter.limit("120/minute")
async def get_one(request: Request, project_id: str):
    return await get_project_by_id(project_id)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("120/minute")
async def delete(request: Request, project_id: str, user_id: str = Depends(get_current_user_id)):
    await delete_project(project_id, user_id)
