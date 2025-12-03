from typing import Optional
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from src.rag.llm import get_llm
from src.rag.vector_db import get_vector_store
from src.trends.schemas import TrendBundle
from src.trends.service import get_trends
from src.utils.schemas import ArtIdeaSet
from src.utils.format_instructions import artIdeaSet_format_instructions

SYSTEM_PROMPT = """
You are an assistant helping a digital artist plan new artwork and Instagram content.

Use BOTH:
- Context about the artist's previous posts, captions, and style notes.
- Current trend information (songs, visual challenges, themes).

Goals:
- Suggest NEW, FRESH ideas that still feel like their style.
- Where possible, connect the ideas to provided trends
  (e.g. suggest using a trending audio or art challenge).
- Do NOT just copy the trends; adapt them to the artist's vibe.

{format_instructions}
"""

def get_style_context(user_hint: Optional[str] = None, k: int = 6) -> str:
    """
    Retrieve relevant documents from the vector DB and format them
    as context text for the LLM.
    """
    vectordb = get_vector_store()
    retriever = vectordb.as_retriever(search_kwargs={"k": k})

    # If user gives a hint (like "cozy autumn vibe"), use that as query
    query = user_hint or "my typical art style, themes, and best performing posts"
    docs = retriever.invoke(query)

    context_chunks = []
    for d in docs:
        meta = d.metadata.get("source", "unknown")
        context_chunks.append(f"[SOURCE: {meta}]\n{d.page_content}")
    return "\n\n".join(context_chunks)

def format_trend_context(bundle: TrendBundle) -> str:
    """
    Convert TrendBundle into a readable text block for the LLM prompt.
    """
    lines = []

    if bundle.songs:
        lines.append("Trending songs / audios:")
        for s in bundle.songs:
            tags_str = ", ".join(s.tags) if s.tags else ""
            lines.append(
                f"- {s.name} by {s.artist} | mood={s.mood or 'unknown'} | tags={tags_str}"
            )

    if bundle.visual_trends:
        lines.append("\nVisual art trends / challenges:")
        for t in bundle.visual_trends:
            tags_str = ", ".join(t.tags) if t.tags else ""
            lines.append(
                f"- {t.name}: {t.description} | tags={tags_str}"
            )

    return "\n".join(lines) if lines else "No trend data available."


def generate_art_ideas(user_hint: Optional[str] = None, num_ideas: int = 3) -> ArtIdeaSet:
    """
    Generate a set of art ideas using:
    - RAG context (artist style, past posts)
    - Trend context (songs + visual trends), optionally filtered by user_hint
    """
    model = get_llm()

    style_context = get_style_context(user_hint=user_hint)

    trend_bundle = get_trends(mood_or_tag=user_hint)
    trend_context = format_trend_context(trend_bundle)

    user_prompt = """
You have access to this context about the artist:

[ARTIST CONTEXT]
{style_context}

And this is the current trend context:

[TRENDS]
{trend_context}

The artist says: "{user_hint} or 'no specific request'"

Generate EXACTLY {num_ideas} ideas that would be exciting for this artist to draw and post on Instagram.
Each idea SHOULD, when reasonable, make use of AT LEAST ONE of the trends above (song or visual trend)
but adapted to the artist's own style.

If a trend doesn't fit their style at all, you can ignore it, but explain this in `why_it_fits_you`.
"""

    template = PromptTemplate(
    template=SYSTEM_PROMPT + user_prompt,
    input_variables=["style_context", "trend_context", "user_hint", "num_ideas"],
    partial_variables={"format_instructions": artIdeaSet_format_instructions()},
)
    parser = PydanticOutputParser(pydantic_object=ArtIdeaSet)

    chain = template | model | parser

    response = chain.invoke({'style_context':style_context, 'trend_context':trend_context,'user_hint':user_hint,'num_ideas':num_ideas})
    
    return response
