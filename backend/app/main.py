from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.api import auth, projects, characters

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(characters.router, prefix="/api/projects/{project_id}/characters", tags=["Characters"])


@app.on_event("startup")
async def startup_event():
    await engine.connect()


@app.on_event("shutdown")
async def shutdown_event():
    await engine.dispose()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.app_version}
