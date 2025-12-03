import json
import sys
from pathlib import Path

# ensure project root is on the path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.instagram.schemas import InstaPost
from src.instagram.service import get_my_posts, get_post_comments



import streamlit as st
from dotenv import load_dotenv
from src.db.models import init_db
from src.db.logging import log_idea_set, log_caption_set, log_comments_and_replies
from src.db.queries import (
    get_recent_ideas,
    get_captions_for_idea,
    get_recent_reply_suggestions,
)
from src.graph.ideation_module import generate_art_ideas
from src.graph.caption_module import generate_captions_for_idea
from src.graph.engagement_module import generate_reply_suggestions
from src.utils.schemas import Comment
from src.analytics.engine import get_analytics_summary_for_prompt


# ---------- INIT ----------

load_dotenv()
init_db()

st.set_page_config(page_title="ArtFlow Studio – Phase 1", layout="wide")
st.title("🎨 ArtFlow Studio – Phase 1")
st.caption("Personal AI assistant for your art ideas, captions & engagement")


# ---------- TABS / SECTIONS ----------

tab1, tab2, tab3 = st.tabs(
    ["💡 Ideas & Captions", "💬 Engagement Assistant", "📜 History Viewer"]
)


# ---------- TAB 1: IDEAS & CAPTIONS ----------

with tab1:
    st.header("💡 Idea + Caption Generator")

    with st.form("idea_form"):
        user_hint = st.text_input(
            "Any mood/focus for your next piece?",
            placeholder="e.g. emotional anime portrait, cozy winter, etc.",
        )
        num_ideas = st.slider("How many ideas?", min_value=1, max_value=10, value=3)
        submitted = st.form_submit_button("Generate ideas")

    if submitted:
        with st.spinner("Generating ideas..."):
            idea_set = generate_art_ideas(
                user_hint=user_hint or None,
                num_ideas=num_ideas,
            )

        if not idea_set.ideas:
            st.error("No ideas generated. Try changing the mood or hint.")
        else:
            # Log ideas to DB
            log_idea_set(idea_set, user_hint=user_hint or None, source="streamlit")

            st.success(f"Generated {len(idea_set.ideas)} ideas.")
            if idea_set.mood_or_focus:
                st.info(f"Overall mood/focus detected: **{idea_set.mood_or_focus}**")

            # Let the user choose one idea
            idea_titles = [
                f"{idx+1}. {idea.title} ({idea.recommended_format}, {idea.difficulty})"
                for idx, idea in enumerate(idea_set.ideas)
            ]
            selected_index = st.selectbox(
                "Pick one idea to generate captions for:",
                options=list(range(len(idea_set.ideas))),
                format_func=lambda i: idea_titles[i],
            )

            chosen_idea = idea_set.ideas[selected_index]

            with st.expander("🔍 View chosen idea details", expanded=True):
                st.markdown(f"**Title:** {chosen_idea.title}")
                st.markdown(f"**ID:** `{chosen_idea.id}`")
                st.markdown(f"**Format:** {chosen_idea.recommended_format}")
                st.markdown(f"**Difficulty:** {chosen_idea.difficulty}")
                st.markdown("**Drawing prompt:**")
                st.write(chosen_idea.drawing_prompt)
                st.markdown("**Style direction:**")
                st.write(chosen_idea.style_direction)
                st.markdown("**Why it fits you:**")
                st.write(chosen_idea.why_it_fits_you)

            if st.button("📝 Generate captions & hashtags for this idea"):
                with st.spinner("Generating captions & hashtags..."):
                    caption_set = generate_captions_for_idea(chosen_idea)

                # Log captions to DB
                log_caption_set(chosen_idea, caption_set)

                st.subheader("📝 Caption options")
                for cap in caption_set.captions:
                    st.write(f"- {cap}")

                st.subheader("🔖 Hashtags")
                st.code(" ".join(caption_set.hashtags))

                if caption_set.timelapse_tips:
                    st.subheader("⏱️ Timelapse tips")
                    for t in caption_set.timelapse_tips:
                        st.write(f"- {t}")

                st.success("Done! Use these for your next timelapse reel/post.")


# ---------- TAB 2: ENGAGEMENT ASSISTANT ----------

with tab2:
    st.header("💬 Engagement Assistant")

    st.write(
        "You can either paste comments manually, or select one of your posts "
        "and (later) fetch comments automatically."
    )

    # Select a post from instagram.service
    st.subheader("Step 1: Choose a post (optional)")
    try:
        ig_posts = get_my_posts(limit=10)
    except Exception as e:
        st.error(f"Error loading IG posts: {e}")
        ig_posts = []

    selected_post_id = None
    if ig_posts:
        post_options = {f"{p.type} | {p.created_at} | {p.caption[:40]}...": p.id for p in ig_posts}
        selected_label = st.selectbox(
            "Select a recent post (optional):",
            options=["(None)"] + list(post_options.keys()),
        )
        if selected_label != "(None)":
            selected_post_id = post_options[selected_label]
            st.info(f"Selected post ID: `{selected_post_id}`")

    # --- Manual comments input ---
    st.subheader("Step 2: Enter comments (or fetch later from IG)")
    default_post_label = selected_post_id or "2024-12-portrait-reel"

    post_id = st.text_input(
        "Post ID / short label (used for logging)",
        value=default_post_label,
    )

    comments_text = st.text_area(
        "Comments (one per line, if you want to paste manually)",
        placeholder="Wow this is amazing!!\nBro this style is fire 🔥\nCan you draw my OC?",
        height=200,
    )

    fetch_from_ig = st.checkbox(
        "Fetch comments from Instagram service for the selected post (if available)",
        value=False,
        help="In mock mode, this uses comments logged in your DB with this post_id. "
             "With real API later, this will call the Graph API."
    )

    if st.button("Generate reply suggestions"):

        from src.utils.schemas import Comment

        # Decide comment source
        comments: list[Comment] = []

        if fetch_from_ig and selected_post_id:
            # Use comments via instagram.service
            try:
                insta_comments = get_post_comments(selected_post_id)
            except Exception as e:
                st.error(f"Error fetching comments from service: {e}")
                insta_comments = []

            if insta_comments:
                for c in insta_comments:
                    comments.append(
                        Comment(
                            id=c.id,
                            text=c.text,
                            author=c.author,
                        )
                    )
            else:
                st.warning("No comments found via service; falling back to manual input.")

        if not comments:
            # Use manual input
            lines = [l.strip() for l in comments_text.split("\n") if l.strip()]
            if not lines:
                st.error("Please either fetch comments or paste at least one comment.")
                st.stop()
        
            comments = [
                Comment(id=f"c{idx+1}", text=text)
                for idx, text in enumerate(lines)
            ]

        # run reply suggestion generation
        with st.spinner("Generating reply suggestions..."):
            batch = generate_reply_suggestions(
                comments=comments,
                post_id=post_id or selected_post_id,
            )

            # Log comments + replies
            log_comments_and_replies(comments, batch, post_id=post_id or selected_post_id)

            st.success("Reply suggestions generated.")

            for reply in batch.replies:
                st.markdown("---")
                st.markdown(f"**Comment ID:** `{reply.comment_id}`")
                st.markdown(f"**Original:** {reply.original_comment}")
                st.markdown("**Suggested replies:**")
                for opt in reply.suggestions:
                    st.write(f"- {opt}")


# ---------- TAB 3: HISTORY VIEWER ----------

with tab3:
    st.header("📜 History Viewer")

    with st.expander("📷 My Instagram posts (via instagram.service)", expanded=False):
        post_limit = st.slider("How many recent posts to load?", 1, 20, 5, key="ig_post_limit")
        try:
            posts: list[InstaPost] = get_my_posts(limit=post_limit)
        except Exception as e:
            st.error(f"Error loading posts: {e}")
            posts = []

        if not posts:
            st.info("No posts available (check posts.json or IG API config).")
        else:
            for p in posts:
                st.markdown("---")
                st.markdown(f"**Post ID:** `{p.id}`")
                st.markdown(f"**Type:** {p.type}")
                st.markdown(f"**Created at:** {p.created_at}")
                st.markdown(f"**Likes:** {p.likes} | **Comments:** {p.comments_count}")
                if p.caption:
                    st.markdown("**Caption:**")
                    st.write(p.caption)
                if p.hashtags:
                    st.markdown("**Hashtags:**")
                    st.code(" ".join(p.hashtags))


    view_choice = st.radio(
        "What do you want to see?",
        options=["Recent ideas", "Captions for idea", "Recent reply suggestions"],
    )
    with st.expander("📈 Overall analytics summary (from posts.json)", expanded=False):
        summary_text = get_analytics_summary_for_prompt()
        st.text(summary_text)


    if view_choice == "Recent ideas":
        limit = st.slider("How many?", 5, 50, 10)
        ideas = get_recent_ideas(limit=limit)
        if not ideas:
            st.info("No ideas logged yet.")
        else:
            for rec in ideas:
                st.markdown("---")
                st.markdown(f"**DB ID:** `{rec.id}` | **Idea ID:** `{rec.idea_id}`")
                st.markdown(f"**Title:** {rec.title}")
                st.markdown(f"**Mood/focus:** {rec.mood_or_focus}")
                st.markdown(f"**User hint:** {rec.user_hint}")
                st.markdown(f"**Source:** {rec.source}")
                st.markdown(f"**Created at (UTC):** {rec.created_at}")
                with st.expander("View prompt & style"):
                    st.markdown("**Drawing prompt:**")
                    st.write(rec.drawing_prompt)
                    st.markdown("**Style direction:**")
                    st.write(rec.style_direction)
                    st.markdown("**Why it fits you:**")
                    st.write(rec.why_it_fits_you)

    elif view_choice == "Captions for idea":
        idea_id_input = st.text_input(
            "Enter idea_id (copy from 'Recent ideas' view):",
            placeholder="e.g. idea_1",
        )
        if st.button("Load captions"):
            if not idea_id_input.strip():
                st.error("Please enter an idea_id.")
            else:
                caps = get_captions_for_idea(idea_id_input.strip())
                if not caps:
                    st.info("No captions stored for this idea yet.")
                else:
                    for rec in caps:
                        st.markdown("---")
                        st.markdown(f"**Record ID:** `{rec.id}`")
                        st.markdown(f"**Created at:** {rec.created_at}")
                        captions = json.loads(rec.captions_json)
                        hashtags = json.loads(rec.hashtags_json)
                        tips = (
                            json.loads(rec.timelapse_tips_json)
                            if rec.timelapse_tips_json
                            else []
                        )
                        st.subheader("Captions")
                        for c in captions:
                            st.write(f"- {c}")
                        st.subheader("Hashtags")
                        st.code(" ".join(hashtags))
                        if tips:
                            st.subheader("Timelapse tips")
                            for t in tips:
                                st.write(f"- {t}")

    elif view_choice == "Recent reply suggestions":
        limit = st.slider("How many?", 5, 50, 10, key="limit_replies")
        replies = get_recent_reply_suggestions(limit=limit)
        if not replies:
            st.info("No reply suggestions logged yet.")
        else:
            for rec in replies:
                st.markdown("---")
                st.markdown(f"**Post ID:** `{rec.post_id}` | **Comment ID:** `{rec.comment_id}`")
                st.markdown(f"**Original comment:** {rec.original_comment}")
                suggestions = json.loads(rec.suggestions_json)
                st.markdown("**Suggestions:**")
                for s in suggestions:
                    st.write(f"- {s}")
                st.markdown(f"**Created at:** {rec.created_at}")
