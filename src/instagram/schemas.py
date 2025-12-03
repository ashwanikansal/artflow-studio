from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class InstaPost(BaseModel):
    id: str = Field(description="Unique identifier for the Instagram post")
    type: str = Field(description="Type of content e.g., reel, image, carousel, etc.")
    caption: str = Field(description="Caption text for the post")
    hashtags: List[str] = Field(default=[], description="List of hashtags used in the post")
    created_at: datetime
    likes: int = Field(default=0, description="Number of likes")
    comments_count: int = Field(default=0, description="Number of comments")


class InstaComment(BaseModel):
    id: str = Field(description="Unique identifier for the comment")
    post_id: str = Field(description="ID of the post this comment belongs to")
    text: str = Field(description="The comment text")
    author: Optional[str] = Field(default=None, description="Author of the comment")
    created_at: Optional[datetime] = Field(default=None, description="Timestamp of when the comment was made")


class InstaPostInsights(BaseModel):
    post_id: str = Field(description="ID of the post")
    likes: int = Field(description="Number of likes")
    comments: int = Field(description="Number of comments")
    # You can extend later: saves, shares, reach, etc.
