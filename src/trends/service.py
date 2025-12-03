from typing import Optional

from .schemas import TrendBundle
from .local_trends import load_trend_bundle, filter_trend_bundle


def get_trends(mood_or_tag: Optional[str] = None) -> TrendBundle:
    """
    Public function to get trends (Phase 2a: from local JSON).
    Later, you can swap implementation to call Spotify/Instagram APIs here.
    """
    bundle = load_trend_bundle()
    return filter_trend_bundle(bundle, mood_or_tag=mood_or_tag)
