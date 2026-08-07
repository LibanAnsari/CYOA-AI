from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from routers import story, job

from db.database import SessionLocal, create_tables

create_tables()  # Create tables if they don't exist

@asynccontextmanager
async def recover_processing_jobs(app: FastAPI):
    db = SessionLocal()
    try:
        recovered_jobs = job.fail_processing_jobs(
            db,
            "The backend restarted while this job was processing. Please start a new story generation request."
        )
        if recovered_jobs:
            print(f"Recovered {recovered_jobs} stale processing job(s) after startup.")
        yield
    finally:
        db.close()


app = FastAPI(
    title="Choose Your Own Adventure Game API",
    description="api to generate cool stories",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=recover_processing_jobs
)

app.add_middleware(
    CORSMiddleware, 
    allow_origins = settings.ALLOWED_ORIGINS,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

app.include_router(story.router, prefix=settings.API_PREFIX)
app.include_router(job.router, prefix=settings.API_PREFIX)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)