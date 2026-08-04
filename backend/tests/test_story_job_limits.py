from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.database import Base
from models.job import StoryJob
from routers.job import fail_processing_jobs
from routers.story import get_active_job_for_session


def test_get_active_job_for_session_returns_only_active_jobs():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as db:
        pending_job = StoryJob(session_id="session-1", theme="A", status="pending")
        processing_job = StoryJob(session_id="session-1", theme="B", status="processing")
        completed_job = StoryJob(session_id="session-1", theme="C", status="completed")
        failed_job = StoryJob(session_id="session-1", theme="D", status="failed")

        db.add_all([pending_job, processing_job, completed_job, failed_job])
        db.commit()

        active_job = get_active_job_for_session(db, "session-1")

        assert active_job is not None
        assert active_job.status == "processing"


def test_fail_processing_jobs_marks_jobs_as_failed():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as db:
        processing_job = StoryJob(session_id="session-1", theme="B", status="processing")
        db.add(processing_job)
        db.commit()

        recovered_count = fail_processing_jobs(db, "Backend restarted")

        db.refresh(processing_job)

        assert recovered_count == 1
        assert processing_job.status == "failed"
        assert processing_job.error == "Backend restarted"
        assert processing_job.completed_at is not None
