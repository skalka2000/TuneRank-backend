from pydantic import BaseModel
from typing import Optional, List, Field

class AlbumCreate(BaseModel):
    title: str
    artist: str
    year: Optional[int] = None
    rating: Optional[float] = Field(default=None, ge=0.0, le=10.0)
 

class SongCreate(BaseModel):
    title: str
    track_number: Optional[int] = None
    rating: Optional[float] = None

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
