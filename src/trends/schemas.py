from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class TrendSong(BaseModel):
    name: str = Field(description="Name of the song")
    artist: str = Field(description="Artist of the song")
    mood: Optional[str] = Field(default=None, description="Mood of the song e.g. emotional, cozy, hype, etc")
    platform: Optional[str] = Field(default=None, description="Platform where this song is trending e.g. instagram, spotify, etc")
    link: Optional[str] = Field(default=None, description="Link for the song")
    tags: List[str] = Field(default=[], description="Tags for the song like, anime, reel, slow, etc")


class VisualTrend(BaseModel):
    name: str = Field(description="Name of the visual trend")
    description: str = Field(description="Description of the visual trend")
    tags: List[str] = Field(default=[], description="Tags for Visual trend like, drawthisinyourstyle, challenge, etc")
    difficulty: Optional[str] = Field(default=None, description="Difficulty of trend from easy, medium, hard.")


class TrendBundle(BaseModel):
    fetched_at: datetime = Field(description="Timestamp when the trends were fetched")
    songs: List[TrendSong] = Field(default=[], description="List of trending songs")
    visual_trends: List[VisualTrend] = Field(default=[], description="List of trending visual trends")
