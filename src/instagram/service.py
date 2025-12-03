from __future__ import annotations

import json
from datetime import datetime, timezone
import os
from pathlib import Path
from typing import List, Optional

from src.instagram.api_client import USER_ID, ig_get
from src.instagram.schemas import InstaPost, InstaComment, InstaPostInsights
from src.db.models import get_session, CommentRecord

# --------------------CONFIG---------------------
DATA_DIR = Path(__file__).parent.parent / "data"
POSTS_PATH = DATA_DIR / "posts.json"

# Toggle between mock (local) and real IG Graph API
USE_REAL_API = os.getenv("USE_REAL_IG_API", "false").lower() == "true"

# ================= MOCK IMPLEMENTATION (LOCAL DATA) =================

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


def get_my_posts_mock(limit: Optional[int] = None) -> List[InstaPost]:
    """
    Return recent posts from local posts.json.
    """
    raw_posts = _load_posts_raw()
    posts = [_parse_post(p) for p in raw_posts]

    # Sort by created_at desc
    posts_sorted = sorted(posts, key=lambda p: p.created_at, reverse=True)

    if limit is not None:
        posts_sorted = posts_sorted[:limit]

    return posts_sorted


def get_post_by_id_mock(post_id: str) -> Optional[InstaPost]:
    raw_posts = _load_posts_raw()
    for p in raw_posts:
        if str(p.get("id")) == str(post_id):
            return _parse_post(p)
    return None


def get_post_insights_mock(post_id: str) -> Optional[InstaPostInsights]:
    """
    Mock: derive insights from posts.json fields (likes & comments only).
    """
    post = get_post_by_id_mock(post_id)
    if post is None:
        return None

    return InstaPostInsights(
        post_id=post.id,
        likes=post.likes,
        comments=post.comments_count,
    )


def get_post_comments_mock(post_id: str, limit: Optional[int] = None) -> List[InstaComment]:
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



# ================= REAL INSTAGRAM GRAPH API IMPLEMENTATION =================

def get_my_posts_live(limit: Optional[int] = None):
    """
    Live version: fetch posts from Instagram Graph API.

    Requires environment variables:
    - INSTAGRAM_ACCESS_TOKEN
    - INSTAGRAM_USER_ID
    configured in instagram/api_client.py and .env
    """
    
    if not USER_ID:
        raise RuntimeError("USER_ID is not set. Check INSTAGRAM_USER_ID in your .env.")
    fields = (
        "id,caption,media_type,media_url,thumbnail_url,"
        "timestamp,like_count,comments_count"
    )
    
    data = ig_get(f"{USER_ID}/media", params={"fields": fields})

    items = data.get("data", [])
    
    posts = []
    for item in items:
        try:
            posts.append(
                InstaPost(
                    id=item["id"],
                    type=item.get("media_type", "unknown"),
                    caption=item.get("caption", ""),
                    hashtags=[h for h in item.get("caption", "").split() if h.startswith("#")],
                    created_at=datetime.fromisoformat(item.get("timestamp")),
                    likes=item.get("like_count", 0),
                    comments_count=item.get("comments_count", 0),
                )
            )
        except Exception as e:
            print("Error parsing post:", e)

    posts_sorted = sorted(posts, key=lambda p: p.created_at, reverse=True)

    if limit:
        posts_sorted = posts_sorted[:limit]

    return posts_sorted

def get_post_by_id_live(post_id: str) -> Optional[InstaPost]:
    """
    Live version: fetch a single media object.
    """
    fields = (
        "id,caption,media_type,media_url,thumbnail_url,"
        "timestamp,like_count,comments_count"
    )
    data = ig_get(post_id, params={"fields": fields})

    if "id" not in data:
        return None

    caption = data.get("caption", "") or ""
    hashtags = [w for w in caption.split() if w.startswith("#")]

    ts = data.get("timestamp")
    try:
        created_at = datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else datetime.utcnow()
    except Exception:
        created_at = datetime.utcnow()

    return InstaPost(
        id=data["id"],
        type=data.get("media_type", "unknown"),
        caption=caption,
        hashtags=hashtags,
        created_at=created_at,
        likes=int(data.get("like_count", 0) or 0),
        comments_count=int(data.get("comments_count", 0) or 0),
    )

def get_post_comments_live(post_id: str, limit: Optional[int] = None):
    """
    Live version: fetch comments from Instagram Graph API.
    """
    fields = "id,text,username,timestamp"

    data = ig_get(f"{post_id}/comments", params={"fields": fields})

    items = data.get("data", [])

    comments: List[InstaComment] = []

    for c in items:
        ts = c.get("timestamp")
        try:
            created_at = datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else None
        except Exception:
            created_at = None

        comments.append(
            InstaComment(
                id=c["id"],
                post_id=post_id,
                text=c.get("text", ""),
                author=c.get("username"),
                created_at=created_at,
            )
        )

    if limit is not None:
        comments = comments[:limit]

    return comments

def get_post_insights_live(post_id: str) -> Optional[InstaPostInsights]:
    """
    Live version: fetch insights metrics for a post.
    NOTE: Requires that your IG account & app have insights permissions
    and that the media type supports insights.
    """
   
    metric = "impressions,reach,likes,comments"

    data = ig_get(f"{post_id}/insights", params={"metric": metric})

    metrics_list = data.get("data", [])
    if not metrics_list:
        # Fallback: try basic post data
        post = get_post_by_id_live(post_id)
        if post is None:
            return None
        return InstaPostInsights(
            post_id=post.id,
            likes=post.likes,
            comments=post.comments_count,
        )

    insights = {}
    for item in metrics_list:
        name = item.get("name")
        values = item.get("values", [])
        if values:
            insights[name] = values[0].get("value", 0)

    # Fallback for likes/comments if not in insights
    post = get_post_by_id_live(post_id)

    return InstaPostInsights(
        post_id=post_id,
        likes=insights.get("likes", post.likes if post else 0),
        comments=insights.get("comments", post.comments_count if post else 0),
    )

# ================= PUBLIC API (SWITCHING BETWEEN MOCK & LIVE) =================

def get_my_posts(limit: Optional[int] = None) -> List[InstaPost]:
    """
    Public function for the rest of the app.

    If USE_REAL_API=true → use live Graph API.
    Else → use local mock posts.json.
    """
    if USE_REAL_API:
        return get_my_posts_live(limit=limit)
    return get_my_posts_mock(limit=limit)


def get_post_by_id(post_id: str) -> Optional[InstaPost]:
    if USE_REAL_API:
        return get_post_by_id_live(post_id)
    return get_post_by_id_mock(post_id)


def get_post_insights(post_id: str) -> Optional[InstaPostInsights]:
    if USE_REAL_API:
        return get_post_insights_live(post_id)
    return get_post_insights_mock(post_id)


def get_post_comments(post_id: str, limit: Optional[int] = None) -> List[InstaComment]:
    if USE_REAL_API:
        return get_post_comments_live(post_id, limit=limit)
    return get_post_comments_mock(post_id, limit=limit)