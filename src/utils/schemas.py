from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal

class ArtIdea(BaseModel):
    id: str = Field(description="Id of the idea")
    title: str = Field(description="The title of the art idea")
    drawing_prompt: str = Field(description="A brief detail of what to draw")
    style_direction: str = Field(description="How to style it like mood, etc.)")
    why_it_fits_you: str = Field(description="Explanation of why this idea fits, based on your past work")
    recommended_format: Literal['reel', 'image post', 'corousel post'] = Field(description="Recommened output format of this idea on instagram")
    difficulty: Literal['easy','medium','hard'] = Field(description="Difficulty of this idea")

    @field_validator("recommended_format", "difficulty", mode="before")
    def normalize_literals(cls, v):
        if isinstance(v, str):
            return v.strip().lower()
        return v

class ArtIdeaSet(BaseModel):
    mood_or_focus: Optional[str] = None
    ideas: List[ArtIdea] = Field(description="List of all the art ideas")

class CaptionSet(BaseModel):
    idea_id: str = Field(description="Id of the idea")
    captions: List[str] = Field(description="List of captions for reel/post")
    hashtags: List[str] = Field(description="List of hastags to be included")
    timelapse_tips: Optional[List[str]] = None

class Comment(BaseModel):
    id: str = Field(description="Id of the comment")
    text: str = Field(description="The comment text")
    author: Optional[str] = None # author name or handle


class ReplySuggestion(BaseModel):
    comment_id: str = Field(description="Id of the comment to reply to")
    original_comment: str = Field(description="The original comment text")
    suggestions: List[str] = Field(description="List of reply suggestions for the comment")


class ReplyBatch(BaseModel):
    post_id: Optional[str] = None
    replies: List[ReplySuggestion] = Field(description="List of reply suggestions for comments")
