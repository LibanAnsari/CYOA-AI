import uuid
from typing import List, Optional
from datetime import datetime, time

from fastapi import APIRouter, Depends, HTTPException, Cookie, Request, Response, BackgroundTasks, logger
from sqlalchemy.orm import Session

from db.database import SessionLocal, get_db

from models.story import Story, StoryNode
from models.job import StoryJob

from schemas.story import CompleteStoryResponse, CompleteStoryNodeResponse, CreateStoryRequest
from schemas.job import StoryJobResponse

from core.story_generator import StoryGenerator
from core.config import settings

router = APIRouter(
    prefix="/stories",
    tags=["stories"]
)


def get_session_id(session_id: Optional[str] = Cookie(None)):
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id


def get_active_job_for_session(db: Session, session_id: str) -> Optional[StoryJob]:
    processing_job = (
        db.query(StoryJob)
        .filter(StoryJob.session_id == session_id, StoryJob.status == "processing")
        .order_by(StoryJob.created_at.desc())
        .first()
    )
    if processing_job:
        return processing_job

def get_completed_jobs_count_for_today(db: Session, identifier: str, mode: str = "session") -> int:
    today = datetime.combine(datetime.now().date(), time.min)
    
    if mode == "session":
        completed_today = db.query(StoryJob).filter(
            StoryJob.session_id == identifier,
            StoryJob.status == "completed",
            StoryJob.completed_at >= today
        ).count()
    elif mode == "ip_address":
        completed_today = db.query(StoryJob).filter(
            StoryJob.ip_address == identifier,
            StoryJob.status == "completed",
            StoryJob.completed_at >= today
        ).count()
    else:
        raise ValueError(f"Unknown mode: {mode}")    
    
    return completed_today

@router.post("/create", response_model=StoryJobResponse)
def create_story(
    http_request: Request,
    request: CreateStoryRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        samesite="lax",
        secure=True,      # when using HTTPS
        max_age=60*60*24*30
    )

    ip_address = http_request.client.host
    print(f"Received story generation request from IP: {ip_address}, session_id: {session_id}, theme: {request.theme}")

    active_job = get_active_job_for_session(db, session_id)
    if active_job:
        raise HTTPException(
            status_code=409,
            detail="A story generation job is already in progress for this session. Please wait for it to complete before starting a new one."
        )
        
    if settings.RATE_LIMIT_ENABLED:
        completed_today_session = get_completed_jobs_count_for_today(db, session_id, mode="session")
        logger.info(f"Session {session_id} has completed {completed_today_session} stories today.")
        if completed_today_session >= settings.SESSION_DAILY_LIMIT:
            raise HTTPException(
                status_code=429,
                detail=f"You have reached your daily story generation limit ({settings.SESSION_DAILY_LIMIT}). Please try again tomorrow."
            )
        
        completed_today_ip = get_completed_jobs_count_for_today(db, ip_address, mode="ip_address")
        logger.info(f"IP {ip_address} has completed {completed_today_ip} stories today.")
        if completed_today_ip >= settings.IP_DAILY_LIMIT:
            raise HTTPException(
                status_code=429,
                detail=f"Daily story generation limit ({settings.IP_DAILY_LIMIT}) reached. Please try again tomorrow."
            )
    
    job_id = str(uuid.uuid4())
    
    job = StoryJob(
        job_id=job_id,
        session_id=session_id,
        ip_address=ip_address,
        theme=request.theme,
        status="pending"
    )
    
    db.add(job)
    db.commit()
    
    background_tasks.add_task(
        generate_story_task,
        job_id=job_id,
        theme=request.theme,
        session_id=session_id
    )
    
    return job


def generate_story_task(job_id: str, theme: str, session_id: str):
    db = SessionLocal()
        
    try:
        job = db.query(StoryJob).filter(StoryJob.job_id == job_id).first()
        
        if not job:
            return
        
        try:
            job.status = "processing"
            db.commit()
            
            story = StoryGenerator.generate_story(db, session_id, theme)
            
            job.story_id = story.id
            job.status = "completed"
            job.completed_at = datetime.now()
            
            db.commit()
        except Exception as e:
            job.status = "failed"
            job.completed_at = datetime.now()
            job.error = str(e)
            db.commit()
        
    finally:
        db.close()
        
            

@router.get("/{story_id}/complete", response_model=CompleteStoryResponse)
def get_complete_story(story_id: int, db: Session = Depends(get_db)):
    
    story = db.query(Story).filter(Story.id == story_id).first()
    
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    complete_story = build_complete_story_tree(db, story)
    
    return complete_story


def build_complete_story_tree(db: Session, story: Story) -> CompleteStoryResponse:
    nodes = db.query(StoryNode).filter(StoryNode.story_id == story.id).all()
    
    node_dict = {}
    for node in nodes:
        node_response = CompleteStoryNodeResponse(
            id=node.id,
            content=node.content,
            is_ending=node.is_ending,
            is_winning_ending=node.is_winning_ending,
            options=node.options
        )
        node_dict[node.id] = node_response
        
    root_node = next((node for node in nodes if node.is_root), None) 
    
    if not root_node:
        raise HTTPException(status_code=500, detail="Root node not found for the story")
    
    return CompleteStoryResponse(
        id=story.id,
        title=story.title,
        theme=story.theme,
        # session_id=story.session_id,
        created_at=story.created_at,
        root_node=node_dict[root_node.id],
        all_nodes=node_dict
    )


@router.get("/all-stories")
def get_all_stories():
    db = SessionLocal()

    completed_jobs = db.query(StoryJob).filter(StoryJob.status == "completed").all()
    complete_stories = []
    for job in completed_jobs:
        story = db.query(Story).filter(Story.id == job.story_id).first()
        if story:
            complete_stories.append({
                "story_id": story.id,
                "title": story.title,
                "theme": story.theme
            })

    db.close()
    
    return complete_stories        