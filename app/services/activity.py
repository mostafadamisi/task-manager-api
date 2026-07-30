from datetime import datetime, timezone
from bson import ObjectId
from app.database import get_db
from app.schemas.activity import ActivityResponse
from app.utils.pagination import paginate


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
    return await paginate(db.activities, query, page, limit, sort_key="timestamp", mapper=doc_to_response)
