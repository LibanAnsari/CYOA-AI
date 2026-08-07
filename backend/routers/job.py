import uuid
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Cookie, Response, BackgroundTasks
from sqlalchemy.orm import Session

from db.database import SessionLocal, get_db

from models.job import StoryJob

from schemas.job import StoryJobResponse


router = APIRouter(
    prefix="/jobs",
    tags=["jobs"]
)


def fail_processing_jobs(db: Session, error_message: str) -> int:
    processing_jobs = db.query(StoryJob).filter(StoryJob.status == "processing" or StoryJob.status == "pending").all()

    for job in processing_jobs:
        job.status = "failed"
        job.error = error_message
        job.completed_at = datetime.now()

    if processing_jobs:
        db.commit()

    return len(processing_jobs)


@router.get("/{job_id}", response_model=StoryJobResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    
    job = db.query(StoryJob).filter(StoryJob.job_id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job