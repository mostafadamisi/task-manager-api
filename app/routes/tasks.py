from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from app.dependencies import get_current_user_id
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.services.task import (
    create_task,
    get_task_by_id,
    update_task,
    delete_task,
    filter_tasks,
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create(data: TaskCreate, user_id: str = Depends(get_current_user_id)):
    return await create_task(data, user_id)


@router.get("/")
async def list_filtered(
    status: Optional[str] = Query(None),
    assignee: Optional[str] = Query(None),
    due_date: Optional[datetime] = Query(None),
    project_id: Optional[str] = Query(None),
):
    return await filter_tasks(status, assignee, due_date, project_id)


@router.get("/{task_id}")
async def get_one(task_id: str):
    return await get_task_by_id(task_id)


@router.put("/{task_id}")
async def update(task_id: str, data: TaskUpdate, user_id: str = Depends(get_current_user_id)):
    return await update_task(task_id, data, user_id)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(task_id: str, user_id: str = Depends(get_current_user_id)):
    await delete_task(task_id, user_id)
