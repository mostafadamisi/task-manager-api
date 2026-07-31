from datetime import datetime, timezone
from typing import Literal, Optional
from bson import ObjectId
from fastapi import HTTPException, status
from app.database import get_db
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.services.activity import create_activity
from app.utils.pagination import paginate
from app.utils.validation import parse_object_id


def doc_to_response(doc) -> TaskResponse:
    return TaskResponse(
        id=str(doc["_id"]),
        title=doc["title"],
        description=doc["description"],
        status=doc["status"],
        due_date=doc.get("due_date"),
        project_id=str(doc["project_id"]),
        assignee=str(doc["assignee"]) if doc.get("assignee") else None,
        created_by=str(doc["created_by"]),
        created_at=doc["created_at"],
    )


async def get_task_or_404(task_id: str) -> dict:
    db = get_db()
    task = await db.tasks.find_one({"_id": parse_object_id(task_id, "task_id")})
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


async def create_task(data: TaskCreate, user_id: str) -> TaskResponse:
    db = get_db()

    project = await db.projects.find_one({"_id": parse_object_id(data.project_id, "project_id")})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    task = {
        "title": data.title,
        "description": data.description,
        "status": data.status,
        "due_date": data.due_date,
        "project_id": ObjectId(data.project_id),
        "assignee": parse_object_id(data.assignee, "assignee") if data.assignee else None,
        "created_by": ObjectId(user_id),
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.tasks.insert_one(task)
    task["_id"] = result.inserted_id
    await create_activity(str(result.inserted_id), user_id, "task.created")
    return doc_to_response(task)


async def get_task_by_id(task_id: str) -> TaskResponse:
    db = get_db()
    task = await db.tasks.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return doc_to_response(task)


def compute_task_changes(old_task: dict, update_data: dict) -> dict | None:
    changes = {}
    for field, new_val in update_data.items():
        if field == "updated_at":
            continue
        old_val = old_task.get(field)
        if str(old_val) != str(new_val):
            changes[field] = {"old": str(old_val) if old_val else None, "new": str(new_val) if new_val else None}
    return changes if changes else None


def classify_task_change_action(changes: dict) -> str:
    return "task.status_changed" if list(changes.keys()) == ["status"] else "task.updated"


async def update_task(task_id: str, data: TaskUpdate) -> TaskResponse:
    db = get_db()
    task = await get_task_or_404(task_id)

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return doc_to_response(task)

    if "assignee" in update_data:
        update_data["assignee"] = (
            parse_object_id(update_data["assignee"], "assignee") if update_data["assignee"] else None
        )

    update_data["updated_at"] = datetime.now(timezone.utc)

    await db.tasks.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": update_data},
    )
    updated = await db.tasks.find_one({"_id": ObjectId(task_id)})
    return doc_to_response(updated), task, update_data


async def delete_task(task_id: str, user_id: str) -> None:
    db = get_db()
    await get_task_or_404(task_id)
    await db.tasks.delete_one({"_id": ObjectId(task_id)})
    await create_activity(task_id, user_id, "task.deleted")


async def filter_tasks(
    status: Optional[Literal["todo", "in_progress", "done"]] = None,
    assignee: str | None = None,
    due_date: datetime | None = None,
    project_id: str | None = None,
    page: int = 1,
    limit: int = 20,
) -> dict:
    db = get_db()
    query = {}

    if status:
        query["status"] = status
    if assignee:
        query["assignee"] = parse_object_id(assignee, "assignee")
    if due_date:
        query["due_date"] = {"$lte": due_date}
    if project_id:
        query["project_id"] = parse_object_id(project_id, "project_id")

    return await paginate(db.tasks, query, page, limit, mapper=doc_to_response)
