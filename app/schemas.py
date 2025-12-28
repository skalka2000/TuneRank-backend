from pydantic import BaseModel
from typing import Optional, List

class AlbumCreate(BaseModel):
    title: str
    artist: str
    year: Optional[int] = None
    rating: Optional[int] = None
 

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
