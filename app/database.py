from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client: AsyncIOMotorClient | None = None
db = None


async def connect_db():
    global client, db
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.DATABASE_NAME]

    await db.users.create_index("email", unique=True)

    await db.tasks.create_index([("project_id", 1), ("status", 1)])
    await db.tasks.create_index([("assignee", 1), ("status", 1)])
    await db.tasks.create_index("due_date")


async def close_db():
    global client
    if client:
        client.close()


def get_db():
    return db
