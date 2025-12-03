import json
from typing import List, Optional
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from src.rag.llm import get_llm
from src.utils.format_instructions import reply_batch_format_instructions
from src.utils.schemas import Comment, ReplySuggestion, ReplyBatch

SYSTEM_PROMPT = """
You are an assistant helping a digital artist reply to comments on Instagram.

Goals:
- Keep replies warm, genuine, and human.
- Vary the wording; don't repeat the same phrase everywhere.
- Keep them short (1–2 lines).
- No spam, no begging ("please follow", "share this", etc.).
- Use natural emojis sometimes, but not too many.
- If the comment is in Hindi or Hinglish, you can reply in that tone too.

{format_instructions}
"""

def generate_reply_suggestions(
    comments: List[Comment],
    post_id: Optional[str] = None,
) -> ReplyBatch:
    """
    Given a list of Comment objects, generate multiple reply suggestions per comment.
    """
    model = get_llm()

    comments_payload = [
        {
            "id": c.id,
            "text": c.text,
            "author": c.author,
        }
        for c in comments
    ]

    comments_json = json.dumps(comments_payload, ensure_ascii=False, indent=2)

    user_prompt = """
Post ID (optional): {post_id}

Here is the list of comments on the artist's post (JSON):

{comments_json}

For EACH comment, create 2–3 reply ideas.
Reply should be in first person, as if the artist is replying directly.
"""

    prompt_template = PromptTemplate(
        template=SYSTEM_PROMPT + user_prompt,
        input_variables=["post_id", "comments_json"],
        partial_variables={"format_instructions": reply_batch_format_instructions()}
    )

    parser = PydanticOutputParser(pydantic_object=ReplyBatch)

    chain = prompt_template | model | parser

    response = chain.invoke({
        "post_id": post_id or "null",
        "comments_json": comments_json,
    })

    return response