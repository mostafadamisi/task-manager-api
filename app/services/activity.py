from datetime import datetime, timezone
from bson import ObjectId
from app.database import get_db
from app.schemas.activity import ActivityResponse


def doc_to_response(doc) -> ActivityResponse:
    return ActivityResponse(
        id=str(doc["_id"]),
        task_id=str(doc["task_id"]),
        user_id=str(doc["user_id"]),
        action=doc["action"],
        changes=doc.get("changes"),
        timestamp=doc["timestamp"],
    )


async def create_activity(
    task_id: str, user_id: str, action: str, changes: dict | None = None
) -> None:
    db = get_db()
    entry = {
        "task_id": ObjectId(task_id),
        "user_id": ObjectId(user_id),
        "action": action,
        "changes": changes,
        "timestamp": datetime.now(timezone.utc),
    }
    await db.activities.insert_one(entry)


async def get_task_activities(
    task_id: str, page: int = 1, limit: int = 20
) -> dict:
    db = get_db()
    query = {"task_id": ObjectId(task_id)}
    skip = (page - 1) * limit
    total = await db.activities.count_documents(query)
    cursor = (
        db.activities.find(query)
        .sort("timestamp", -1)
        .skip(skip)
        .limit(limit)
    )
    items = []
    async for doc in cursor:
        items.append(doc_to_response(doc))
    pages = (total + limit - 1) // limit
    return {"items": items, "total": total, "page": page, "limit": limit, "pages": pages}
