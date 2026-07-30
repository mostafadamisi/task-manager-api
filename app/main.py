from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from app.database import connect_db, close_db
from app.dependencies import limiter
from app.routes.activity import router as activity_router
from app.routes.auth import router as auth_router
from app.routes.projects import router as projects_router
from app.routes.tasks import router as tasks_router

app = FastAPI(title="Task Manager API")
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(tasks_router)
app.include_router(activity_router)


@app.on_event("startup")
async def startup():
    await connect_db()


@app.on_event("shutdown")
async def shutdown():
    await close_db()


@app.get("/health")
async def health_check():
    return {"status": "ok"}
