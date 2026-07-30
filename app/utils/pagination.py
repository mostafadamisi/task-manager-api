from pydantic import BaseModel, Field


class PageParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)


async def paginate(collection, query: dict, page: int, limit: int, sort_key: str = "created_at", mapper=None):
    skip = (page - 1) * limit
    total = await collection.count_documents(query)
    cursor = collection.find(query).sort(sort_key, -1).skip(skip).limit(limit)
    items = []
    async for doc in cursor:
        items.append(mapper(doc) if mapper else doc)
    pages = (total + limit - 1) // limit
    return {"items": items, "total": total, "page": page, "limit": limit, "pages": pages}
