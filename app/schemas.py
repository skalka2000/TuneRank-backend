from pydantic import BaseModel, Field
from typing import Optional, List

class AlbumCreate(BaseModel):
    title: str
    artist: str
    year: Optional[int] = None
    rating: Optional[float] = Field(default=None, ge=0.0, le=10.0)
 

class SongCreate(BaseModel):
    title: str
    track_number: Optional[int] = Field(default=None, ge=1)
    rating: Optional[float] = Field(default=None, ge=0.0, le=11.0)

class Song(BaseModel):
    id: int
    title: str
    track_number: Optional[int]
    rating: Optional[float]
    album_id: int

    class Config:
        orm_mode = True

class Album(BaseModel):
    id: int
    title: str
    artist: str
    year: Optional[int]
    rating: Optional[float]
    songs: List[Song] = []

    class Config:
        orm_mode = True

from typing import Optional

class AlbumUpdate(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    year: Optional[int] = None
    rating: Optional[float] = Field(default=None, ge=0.0, le=10.0)

class SongUpdate(BaseModel):
    title: Optional[str] = None
    track_number: Optional[int] = Field(default=None, ge=1)
    rating: Optional[float] = Field(default=None, ge=0.0, le=11.0)
