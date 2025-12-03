from typing import List, Optional

from sqlmodel import select

from src.db.models import (
    get_session,
    IdeaRecord,
    CaptionRecord,
    ReplySuggestionRecord,
)

def get_recent_ideas(limit: int = 10) -> List[IdeaRecord]:
    with get_session() as session:
        stmt = (
            select(IdeaRecord)
            .order_by(IdeaRecord.created_at.desc())
            .limit(limit)
        )
        return list(session.exec(stmt))

def get_captions_for_idea(idea_id: str) -> List[CaptionRecord]:
    with get_session() as session:
        stmt = (
            select(CaptionRecord)
            .where(CaptionRecord.idea_id == idea_id)
            .order_by(CaptionRecord.created_at.desc())
        )
        return list(session.exec(stmt))

def get_recent_reply_suggestions(limit: int = 10) -> List[ReplySuggestionRecord]:
    with get_session() as session:
        stmt = (
            select(ReplySuggestionRecord)
            .order_by(ReplySuggestionRecord.created_at.desc())
            .limit(limit)
        )
        return list(session.exec(stmt))
