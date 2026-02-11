from pydantic import BaseModel, Field
from typing import Optional, List

class SongCreate(BaseModel):
    title: str
    track_number: Optional[int] = Field(default=None, ge=1)
    rating: Optional[float] = Field(default=None, ge=0.0, le=11.0)
    is_interlude: Optional[bool] = False

class AlbumCreate(BaseModel):
    title: str
    artist: str
    year: Optional[int] = None
    rating: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    songs: Optional[List[SongCreate]] = []

class AlbumBase(BaseModel):
    id: int
    title: str
    artist: str
    year: Optional[int]
    rating: Optional[float]
    average_rating: Optional[float] = None
    overall_rating: Optional[float] = None

    model_config = {
        "from_attributes": True
    }


class Song(BaseModel):
    id: int
    title: str
    track_number: Optional[int]
    rating: Optional[float]
    album_id: int
    album: Optional[AlbumBase]
    is_interlude: Optional[bool] = False
    user_id: int

    model_config = {
        "from_attributes": True
    }


class Album(BaseModel):
    id: int
    title: str
    artist: str
    year: Optional[int]
    rating: Optional[float]
    songs: List[Song] = []
    average_rating: Optional[float] = None
    overall_rating: Optional[float] = None    
    user_id: int

    model_config = {
        "from_attributes": True
}


class AlbumUpdate(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    year: Optional[int] = None
    rating: Optional[float] = Field(default=None, ge=0.0, le=10.0)

class SongUpdate(BaseModel):
    title: Optional[str] = None
    track_number: Optional[int] = Field(default=None, ge=1)
    rating: Optional[float] = Field(default=None, ge=0.0, le=11.0)
    is_interlude: Optional[bool] = False


class UserSettingsBase(BaseModel):
    average_power: float = 1.0
    greatness_threshold: float = 8.0
    scaling_factor: float = 0.3
    steep_factor: float = 3.0
    average_rating_weight: float = 0.5


class UserSettingsCreate(UserSettingsBase):
    pass


class UserSettings(UserSettingsBase):
    id: int
    user_id: int

    model_config = {
        "from_attributes": True
    }
