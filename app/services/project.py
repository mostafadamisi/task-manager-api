from datetime import datetime, timezone
from bson import ObjectId
from fastapi import HTTPException, status
from app.database import get_db
from app.schemas.project import ProjectCreate, ProjectResponse


def doc_to_response(doc) -> ProjectResponse:
    return ProjectResponse(
        id=str(doc["_id"]),
        name=doc["name"],
        description=doc["description"],
        owner=str(doc["owner"]),
        members=[str(m) for m in doc["members"]],
        created_at=doc["created_at"],
    )


async def get_project_or_404(project_id: str) -> dict:
    db = get_db()
    p = await db.projects.find_one({"_id": ObjectId(project_id)})
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return p


async def create_project(data: ProjectCreate, user_id: str) -> ProjectResponse:
    db = get_db()
    project = {
        "name": data.name,
        "description": data.description,
        "owner": ObjectId(user_id),
        "members": [ObjectId(m) for m in data.members],
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.projects.insert_one(project)
    return ProjectResponse(
        id=str(result.inserted_id),
        name=data.name,
        description=data.description,
        owner=user_id,
        members=data.members,
        created_at=project["created_at"],
    )


async def get_all_projects(page: int = 1, limit: int = 20) -> dict:
    db = get_db()
    skip = (page - 1) * limit
    total = await db.projects.count_documents({})
    cursor = db.projects.find().sort("created_at", -1).skip(skip).limit(limit)
    projects = []
    async for p in cursor:
        projects.append(doc_to_response(p))
    pages = (total + limit - 1) // limit
    return {"items": projects, "total": total, "page": page, "limit": limit, "pages": pages}


async def get_project_by_id(project_id: str) -> ProjectResponse:
    p = await get_project_or_404(project_id)
    return doc_to_response(p)


async def delete_project(project_id: str, user_id: str) -> None:
    db = get_db()
    p = await get_project_or_404(project_id)
    if str(p["owner"]) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can delete this project",
        )
    await db.projects.delete_one({"_id": ObjectId(project_id)})
