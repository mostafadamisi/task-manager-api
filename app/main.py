from fastapi import FastAPI
from app.database import connect_db, close_db
from app.routes.auth import router as auth_router

app = FastAPI(title="Task Manager API")

app.include_router(auth_router)


@app.on_event("startup")
async def startup():
    await connect_db()


@app.on_event("shutdown")
async def shutdown():
    await close_db()


@app.get("/health")
async def health_check():
    return {"status": "ok"}
