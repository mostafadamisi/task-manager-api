from fastapi import APIRouter, Depends, Query, Request, status
from app.dependencies import get_current_user_id, limiter
from app.services.activity import get_task_activities

router = APIRouter(tags=["Activities"])


@router.get("/tasks/{task_id}/activity")
@limiter.limit("120/minute")
async def list_activity(
    request: Request,
    task_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
):
    return await get_task_activities(task_id, page, limit)
