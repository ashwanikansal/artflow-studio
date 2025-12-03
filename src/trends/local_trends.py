from datetime import datetime
from pathlib import Path
import json
from typing import Optional

from .schemas import TrendSong, VisualTrend, TrendBundle

DATA_DIR = Path(__file__).parent.parent / "data"
TRENDS_PATH = DATA_DIR / "trends.json"

def load_trends_raw() -> dict:
    if not TRENDS_PATH.exists():
        raise FileNotFoundError(f"trends.json not found at {TRENDS_PATH}")
    with open(TRENDS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_trend_bundle() -> TrendBundle:
    data = load_trends_raw()
    songs = [TrendSong(**s) for s in data.get("songs", [])]
    vtrends = [VisualTrend(**t) for t in data.get("visual_trends", [])]
    return TrendBundle(
        fetched_at=datetime.utcnow(),
        songs=songs,
        visual_trends=vtrends,
    )


def filter_trend_bundle(
    bundle: TrendBundle,
    mood_or_tag: Optional[str] = None,
) -> TrendBundle:
    """
    Filter songs and visual trends by mood or tag (case-insensitive).
    """
    if not mood_or_tag:
        return bundle

    key = mood_or_tag.lower()

    filtered_songs = [
        s for s in bundle.songs
        if (s.mood and key in s.mood.lower())
        or any(key in tag.lower() for tag in s.tags)
    ]

    filtered_vtrends = [
        t for t in bundle.visual_trends
        if any(key in tag.lower() for tag in t.tags)
    ]

    # If filter removes everything, just return original bundle
    if not filtered_songs and not filtered_vtrends:
        return bundle

    return TrendBundle(
        fetched_at=bundle.fetched_at,
        songs=filtered_songs,
        visual_trends=filtered_vtrends,
    )
