from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils import calculate_weighted_average

class Album(Base):
    __tablename__ = "albums"  # SQL table name

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    year = Column(Integer)
    rating = Column(Float)

    songs = relationship("Song", back_populates="album", cascade="all, delete-orphan")

    @property
    def average_rating(self):
        power = getattr(self, "_average_power", 1.0)
        return calculate_weighted_average(self.songs, power)

    @property
    def overall_rating(self):
        if self.rating is not None and self.average_rating is not None:
            return round((self.rating + self.average_rating) / 2, 2)
        return None


class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    album_id = Column(Integer, ForeignKey("albums.id", ondelete="CASCADE"))
    title = Column(String, nullable=False)
    track_number = Column(Integer)
    rating = Column(Float)
    is_interlude = Column(Boolean, default=False)

    album = relationship("Album", back_populates="songs")

