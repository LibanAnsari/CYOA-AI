from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.database import Base
from models.job import StoryJob
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
