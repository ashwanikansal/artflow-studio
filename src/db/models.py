from datetime import datetime, timezone
from typing import Optional

from sqlmodel import SQLModel, Field, create_engine, Session

# ---- DB CONFIG ----

DATABASE_URL = "sqlite:///./src/db/artflow.db"
engine = create_engine(DATABASE_URL, echo=False)  # echo=True if you want SQL logs

def get_session() -> Session:
    return Session(engine)

def init_db():
    SQLModel.metadata.create_all(engine)

def utc_now():
    return datetime.now(timezone.utc)

# ---- TABLE MODELS ----

class IdeaRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    idea_id: str = Field(index=True)  # LLM idea.id
    title: str
    drawing_prompt: str
    style_direction: str
    why_it_fits_you: str
    recommended_format: str
    difficulty: str
    mood_or_focus: Optional[str] = None
    user_hint: Optional[str] = None
    source: str = "cli"       # e.g. "cli", "web"
    created_at: datetime = Field(default_factory=utc_now)


class CaptionRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    idea_id: str = Field(index=True)
    captions_json: str        # JSON string of list[str]
    hashtags_json: str        # JSON string of list[str]
    timelapse_tips_json: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)


class CommentRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: Optional[str] = Field(default=None, index=True)
    comment_id: str = Field(index=True)
    text: str
    author: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)


class ReplySuggestionRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: Optional[str] = Field(default=None, index=True)
    comment_id: str = Field(index=True)
    original_comment: str
    suggestions_json: str     # JSON string of list[str]
    created_at: datetime = Field(default_factory=utc_now)
