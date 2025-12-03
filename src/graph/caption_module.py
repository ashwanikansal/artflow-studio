# src/graph/caption_module.py

import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from src.rag.llm import get_llm
from src.utils.schemas import CaptionSet

SYSTEM_PROMPT = """
You are an assistant that writes Instagram captions and hashtags for a digital artist.

Rules:
- Keep captions short (1–3 lines).
- Tone: artistic, clean, emotional, minimal.
- Avoid engagement baiting like "follow for more".
- Hashtags must be niche + broad combined (max 5).
- Captions must feel aligned with the artist’s style.
{format_instructions}
"""

def generate_captions_for_idea(idea) -> CaptionSet:
    """
    idea: ArtIdea object
    """
    model = get_llm()

    parser = PydanticOutputParser(pydantic_object=CaptionSet)

    user_prompt = """
Idea ID: {id}
Title: {title}
Drawing prompt: {drawing_prompt}
Style direction: {style_direction}

Create 2–3 caption options + 3 hashtags + simple timelapse video tips.
Tone: minimal, emotional, aesthetic.

Output MUST have all the fields described in output schema.
Use the above Idea ID in output.
"""

    template = PromptTemplate(
    template=SYSTEM_PROMPT + user_prompt,
    input_variables=["id", "title", "drawing_prompt", "style_direction"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = template | model | parser
    response = chain.invoke({
        "id": idea.id,
        "title": idea.title,
        "drawing_prompt": idea.drawing_prompt,
        "style_direction": idea.style_direction
    })
    return response
