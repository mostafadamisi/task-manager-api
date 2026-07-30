from fastapi import APIRouter, Depends, status
from app.dependencies import get_current_user_id
from app.schemas.project import ProjectCreate, ProjectResponse
from app.services.project import create_project, get_all_projects, get_project_by_id, delete_project

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create(data: ProjectCreate, user_id: str = Depends(get_current_user_id)):
    return await create_project(data, user_id)


@router.get("/")
async def list_all():
    return await get_all_projects()


@router.get("/{project_id}")
async def get_one(project_id: str):
    return await get_project_by_id(project_id)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(project_id: str, user_id: str = Depends(get_current_user_id)):
    await delete_project(project_id, user_id)
