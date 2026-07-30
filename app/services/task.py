from datetime import datetime, timezone
from bson import ObjectId
from fastapi import HTTPException, status
from app.database import get_db
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.services.activity import create_activity


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


async def create_task(data: TaskCreate, user_id: str) -> TaskResponse:
    db = get_db()

    project = await db.projects.find_one({"_id": ObjectId(data.project_id)})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    task = {
        "title": data.title,
        "description": data.description,
        "status": data.status,
        "due_date": data.due_date,
        "project_id": ObjectId(data.project_id),
        "assignee": ObjectId(data.assignee) if data.assignee else None,
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


async def update_task(task_id: str, data: TaskUpdate, user_id: str) -> TaskResponse:
    db = get_db()

    task = await db.tasks.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return doc_to_response(task)

    if "assignee" in update_data:
        update_data["assignee"] = ObjectId(update_data["assignee"]) if update_data["assignee"] else None

    update_data["updated_at"] = datetime.now(timezone.utc)

    await db.tasks.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": update_data},
    )
    updated = await db.tasks.find_one({"_id": ObjectId(task_id)})

    changes = {}
    for field in update_data:
        if field == "updated_at":
            continue
        old_val = task.get(field)
        new_val = updated.get(field)
        if str(old_val) != str(new_val):
            changes[field] = {"old": str(old_val) if old_val else None, "new": str(new_val) if new_val else None}

    if changes:
        action = "task.status_changed" if list(changes.keys()) == ["status"] else "task.updated"
        await create_activity(task_id, user_id, action, changes)

    return doc_to_response(updated)


async def delete_task(task_id: str, user_id: str) -> None:
    db = get_db()
    task = await db.tasks.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    await db.tasks.delete_one({"_id": ObjectId(task_id)})
    await create_activity(task_id, user_id, "task.deleted")


async def filter_tasks(
    status: str | None = None,
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
        query["assignee"] = ObjectId(assignee)
    if due_date:
        query["due_date"] = {"$lte": due_date}
    if project_id:
        query["project_id"] = ObjectId(project_id)

    skip = (page - 1) * limit
    total = await db.tasks.count_documents(query)
    cursor = db.tasks.find(query).sort("created_at", -1).skip(skip).limit(limit)
    tasks = []
    async for t in cursor:
        tasks.append(doc_to_response(t))
    pages = (total + limit - 1) // limit
    return {"items": tasks, "total": total, "page": page, "limit": limit, "pages": pages}
