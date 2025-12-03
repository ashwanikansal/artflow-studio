from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from src.instagram.schemas import InstaPost, InstaComment, InstaPostInsights
from src.db.models import get_session, CommentRecord


DATA_DIR = Path(__file__).parent.parent / "data"
POSTS_PATH = DATA_DIR / "posts.json"


def _load_posts_raw() -> list[dict]:
    if not POSTS_PATH.exists():
        return []
    with open(POSTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _parse_post(raw: dict) -> InstaPost:
    # posts.json has created_at as string; parse to datetime
    created_at_str = raw.get("created_at") or raw.get("createdAt") or ""
    try:
        created_at = datetime.fromisoformat(created_at_str)
    except Exception:
        created_at = datetime.now(timezone.utc)

    hashtags = raw.get("hashtags") or []
    if isinstance(hashtags, str):
        # if stored as one string like "#a #b"
        hashtags = [h for h in hashtags.split() if h.startswith("#")]

    return InstaPost(
        id=str(raw.get("id")),
        type=raw.get("type", "unknown"),
        caption=raw.get("caption", ""),
        hashtags=hashtags,
        created_at=created_at,
        likes=int(raw.get("likes", 0) or 0),
        comments_count=int(raw.get("comments", 0) or 0),
    )


# ------------- PUBLIC INTERFACE -------------


def get_my_posts(limit: Optional[int] = None) -> List[InstaPost]:
    """
    Return recent posts from local posts.json.
    Later: replace internals with Instagram Graph API calls.
    """
    raw_posts = _load_posts_raw()
    posts = [_parse_post(p) for p in raw_posts]

    # Sort by created_at desc
    posts_sorted = sorted(posts, key=lambda p: p.created_at, reverse=True)

    if limit is not None:
        posts_sorted = posts_sorted[:limit]

    return posts_sorted


def get_post_by_id(post_id: str) -> Optional[InstaPost]:
    raw_posts = _load_posts_raw()
    for p in raw_posts:
        if str(p.get("id")) == str(post_id):
            return _parse_post(p)
    return None


def get_post_insights(post_id: str) -> Optional[InstaPostInsights]:
    """
    For now, we derive insights from posts.json fields.
    Later: call Graph API /insights endpoint here.
    """
    post = get_post_by_id(post_id)
    if post is None:
        return None

    return InstaPostInsights(
        post_id=post.id,
        likes=post.likes,
        comments=post.comments_count,
    )


def get_post_comments(post_id: str, limit: Optional[int] = None) -> List[InstaComment]:
    """
    Phase 2 mock: read comments from SQLite (CommentRecord) if you used Engagement Assistant.
    If none logged, returns [].
    Later: call Instagram API to fetch real comments.
    """
    from sqlmodel import select

    with get_session() as session:
        stmt = (
            select(CommentRecord)
            .where(CommentRecord.post_id == post_id)
            .order_by(CommentRecord.created_at.asc())
        )
        records = list(session.exec(stmt))

    comments: List[InstaComment] = []
    for rec in records:
        comments.append(
            InstaComment(
                id=rec.comment_id,
                post_id=rec.post_id or post_id,
                text=rec.text,
                author=rec.author,
                created_at=rec.created_at,
            )
        )

    if limit is not None:
        comments = comments[:limit]

    return comments
