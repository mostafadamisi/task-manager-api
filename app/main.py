from fastapi import FastAPI
from app.database import connect_db, close_db
from app.routes.auth import router as auth_router
from app.routes.projects import router as projects_router

app = FastAPI(title="Task Manager API")

app.include_router(auth_router)
app.include_router(projects_router)


@app.on_event("startup")
async def startup():
    await connect_db()


@app.on_event("shutdown")
async def shutdown():
    await close_db()


@app.get("/health")
async def health_check():
    return {"status": "ok"}
