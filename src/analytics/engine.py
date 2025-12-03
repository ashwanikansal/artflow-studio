import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import Tuple

DATA_DIR = Path(__file__).parent.parent / "data"
POSTS_PATH = DATA_DIR / "posts.json"


def load_posts() -> list[dict]:
    if not POSTS_PATH.exists():
        return []
    with open(POSTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_basic_stats(posts: list[dict]) -> Tuple[str, dict]:
    """
    Returns (summary_text, raw_stats_dict)
    """
    if not posts:
        return "No historical posts available for analytics.", {}

    total_likes = 0
    total_comments = 0
    type_counts = Counter()
    hashtag_counts = Counter()
    likes_by_type = defaultdict(list)

    for p in posts:
        likes = int(p.get("likes", 0) or 0)
        comments = int(p.get("comments", 0) or 0)
        p_type = p.get("type", "unknown")
        tags = p.get("hashtags", [])

        total_likes += likes
        total_comments += comments
        type_counts[p_type] += 1
        likes_by_type[p_type].append(likes)
        for h in tags:
            hashtag_counts[h.lower()] += 1

    n = len(posts)
    avg_likes = total_likes / n
    avg_comments = total_comments / n

    # Top hashtags
    top_hashtags = hashtag_counts.most_common(10)

    # Avg likes by type
    avg_likes_by_type = {
        t: (sum(lst) / len(lst)) if lst else 0.0
        for t, lst in likes_by_type.items()
    }

    # Build a plain-text summary for the LLM
    lines = []
    lines.append(f"You have {n} historical posts.")
    lines.append(f"Average likes per post: {avg_likes:.1f}")
    lines.append(f"Average comments per post: {avg_comments:.1f}")

    if avg_likes_by_type:
        lines.append("\nAverage likes by type:")
        for t, v in avg_likes_by_type.items():
            lines.append(f"- {t}: {v:.1f} likes on average")

    if top_hashtags:
        lines.append("\nTop hashtags you have used (by frequency, not necessarily performance):")
        for tag, count in top_hashtags:
            lines.append(f"- {tag}: used {count} times")

    summary = "\n".join(lines)

    raw_stats = {
        "avg_likes": avg_likes,
        "avg_comments": avg_comments,
        "avg_likes_by_type": avg_likes_by_type,
        "top_hashtags": top_hashtags,
        "total_posts": n,
    }

    return summary, raw_stats


def get_analytics_summary_for_prompt() -> str:
    """
    Public function: returns a human-readable analytics summary to feed into prompts.
    """
    posts = load_posts()
    summary, _ = compute_basic_stats(posts)
    return summary
