import json
from pathlib import Path
import sys
from src.db.models import init_db
from src.graph.caption_module import generate_captions_for_idea
from src.graph.engagement_module import generate_reply_suggestions
from src.graph.ideation_module import generate_art_ideas
from src.rag.pipeline import build_rag_chain
from src.utils.schemas import ArtIdea, Comment
from src.db.logging import log_idea_set, log_caption_set, log_comments_and_replies
from src.db.queries import (get_recent_ideas, get_captions_for_idea, get_recent_reply_suggestions)

sys.path.append(str(Path(__file__).resolve().parents[1]))

# ask about art style and past posts
def ask_art_rag():
    chain = build_rag_chain()
    print("🎨 Art RAG Assistant ready. Ask about your art/style or type 'exit'.")
    while True:
        question = input("\nYou: ")
        if question.lower().strip() in {"exit", "quit"}:
            break
        response = chain.invoke({"question": question})
        print("\nAssistant:", response.content)

# generate art ideas and captions CLI
def ideas_and_captions_cli():
    print("🎨 Art Idea Generator")
    print("---------------------")
    user_hint = input("Any specific mood/focus (enter to skip, e.g. 'cozy', 'dark', 'anime girl in rain'):\n> ")
    if not user_hint.strip():
        user_hint = None

    idea_set = generate_art_ideas(user_hint=user_hint, num_ideas=3)

    if not idea_set.ideas:
        print("No ideas generated.")
        return

    # LOG ideas to DB
    log_idea_set(idea_set, user_hint=user_hint or None, source="cli")

    print("\n✨ Generated Ideas ✨")
    if idea_set.mood_or_focus:
        print(f"Mood/focus: {idea_set.mood_or_focus}\n")

    for idea in idea_set.ideas:
        print(f"ID: {idea.id}")
        print(f"Title: {idea.title}")
        print(f"Format: {idea.recommended_format} | Difficulty: {idea.difficulty}")
        print(f"Drawing prompt:\n  {idea.drawing_prompt}")
        print(f"Style direction:\n  {idea.style_direction}")
        print(f"Why it fits you:\n  {idea.why_it_fits_you}")
        print("-" * 50)

    # Optionally generate captions for any idea
    user_choice = input("\nGenerate captions for any idea ID? (enter ID or 'no'):\n> ")
    if user_choice.lower().strip() != 'no':
        matching_ideas = [idea for idea in idea_set.ideas if idea.id == user_choice.strip()]
        if matching_ideas:
            caption_set = generate_captions_for_idea(matching_ideas[0])

            # LOG captions to DB
            log_caption_set(matching_ideas[0], caption_set)
            print(caption_set)
        else:
            print("No matching idea ID found.")

# load sample comments from JSON and generate reply suggestions
def generate_comment_replies_cli():
    with open("src/data/comments.json", "r", encoding="utf-8") as f:
        raw_comments = json.load(f)

    comments = [Comment(**c) for c in raw_comments]

    post_id="post_987"

    reply_batch = generate_reply_suggestions(
        comments=comments,
        post_id=post_id,
    )

    print("\n💬 Reply Suggestions:")
    for reply in reply_batch.replies:
        print(f"\nOriginal Comment: {reply.original_comment}")
        for idx, suggestion in enumerate(reply.suggestions, start=1):
            print(f"  Option {idx}: {suggestion}")

    # LOG comments + replies to DB
    log_comments_and_replies(comments, reply_batch, post_id=post_id)

# view history of ideas, captions, replies
def run_history_viewer():
    print("📜 History Viewer")
    print("-----------------")
    print("1) Recent ideas")
    print("2) Captions for a specific idea")
    print("3) Recent reply suggestions")
    print("q) Back")

    choice = input("Choose an option: ").strip().lower()

    if choice == "1":
        ideas = get_recent_ideas(limit=10)
        if not ideas:
            print("No ideas logged yet.")
            return
        print("\nLast ideas:")
        for rec in ideas:
            print("-" * 50)
            print(f"DB ID: {rec.id} | Idea ID: {rec.idea_id}")
            print(f"Title: {rec.title}")
            print(f"Mood/focus: {rec.mood_or_focus}")
            print(f"Hint: {rec.user_hint}")
            print(f"Created at (UTC): {rec.created_at}")
        print("-" * 50)

    elif choice == "2":
        idea_id = input("Enter idea_id (from ‘Recent ideas’):\n> ").strip()
        caps = get_captions_for_idea(idea_id)
        if not caps:
            print("No captions found for that idea.")
            return
        print(f"\nCaptions for idea_id={idea_id}:")
        for rec in caps:
            print("-" * 50)
            print(f"Record ID: {rec.id} | Created at: {rec.created_at}")
            captions = json.loads(rec.captions_json)
            hashtags = json.loads(rec.hashtags_json)
            tips = json.loads(rec.timelapse_tips_json) if rec.timelapse_tips_json else []
            print("\nCaptions:")
            for c in captions:
                print(f"- {c}")
            print("\nHashtags:")
            print(" ".join(hashtags))
            if tips:
                print("\nTimelapse tips:")
                for t in tips:
                    print(f"- {t}")
        print("-" * 50)

    elif choice == "3":
        replies = get_recent_reply_suggestions(limit=10)
        if not replies:
            print("No reply suggestions logged yet.")
            return
        print("\nRecent reply suggestions:")
        for rec in replies:
            print("-" * 50)
            print(f"Post ID: {rec.post_id} | Comment ID: {rec.comment_id}")
            print(f"Original: {rec.original_comment}")
            suggestions = json.loads(rec.suggestions_json)
            print("Suggestions:")
            for s in suggestions:
                print(f"- {s}")
            print(f"Created at: {rec.created_at}")
        print("-" * 50)

    else:
        return

if __name__ == "__main__":
    # init_db()
    # ask_art_rag()
    ideas_and_captions_cli()
    # generate_comment_replies_cli()
    # run_history_viewer()
