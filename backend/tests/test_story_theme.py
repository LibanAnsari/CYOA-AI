from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.database import Base
from models.story import Story


def test_story_theme_is_stored_and_returned():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as db:
        story = Story(title="Lost Signal", theme="Space mystery", session_id="session-1")
        db.add(story)
        db.commit()

        stored_story = db.query(Story).filter(Story.id == story.id).one()
        assert stored_story.theme == "Space mystery"
