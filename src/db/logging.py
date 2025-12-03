import json
from typing import List, Optional

from src.db.models import (
    get_session,
    IdeaRecord,
    CaptionRecord,
    CommentRecord,
    ReplySuggestionRecord,
)

from src.utils.schemas import ArtIdeaSet, ArtIdea, CaptionSet, Comment, ReplyBatch


# ---- IDEA LOGGING ----

def log_idea_set(
    idea_set: ArtIdeaSet,
    user_hint: Optional[str] = None,
    source: str = "cli",
) -> None:
    """
    Store all generated ideas in the DB.
    """
    with get_session() as session:
        for idea in idea_set.ideas:
            record = IdeaRecord(
                idea_id=idea.id,
                title=idea.title,
                drawing_prompt=idea.drawing_prompt,
                style_direction=idea.style_direction,
                why_it_fits_you=idea.why_it_fits_you,
                recommended_format=idea.recommended_format,
                difficulty=idea.difficulty,
                mood_or_focus=idea_set.mood_or_focus,
                user_hint=user_hint,
                source=source,
            )
            session.add(record)
        session.commit()


# ---- CAPTION LOGGING ----

def log_caption_set(
    idea: ArtIdea,
    caption_set: CaptionSet,
) -> None:
    """
    Store the captions & hashtags for a given idea.
    """
    with get_session() as session:
        record = CaptionRecord(
            idea_id=idea.id,
            captions_json=json.dumps(caption_set.captions, ensure_ascii=False),
            hashtags_json=json.dumps(caption_set.hashtags, ensure_ascii=False),
            timelapse_tips_json=(
                json.dumps(caption_set.timelapse_tips, ensure_ascii=False)
                if caption_set.timelapse_tips is not None
                else None
            ),
        )
        session.add(record)
        session.commit()


# ---- ENGAGEMENT LOGGING ----

def log_comments_and_replies(
    comments: List[Comment],
    reply_batch: ReplyBatch,
    post_id: Optional[str] = None,
) -> None:
    """
    Store original comments and reply suggestions.
    """
    with get_session() as session:
        # Save comments
        for c in comments:
            c_rec = CommentRecord(
                post_id=post_id,
                comment_id=c.id,
                text=c.text,
                author=c.author,
            )
            session.add(c_rec)

        # Save reply suggestions
        for r in reply_batch.replies:
            r_rec = ReplySuggestionRecord(
                post_id=post_id or reply_batch.post_id,
                comment_id=r.comment_id,
                original_comment=r.original_comment,
                suggestions_json=json.dumps(r.suggestions, ensure_ascii=False),
            )
            session.add(r_rec)

        session.commit()
