from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

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
        rated = [s.rating for s in self.songs if s.rating is not None]
        if rated:
            return round(sum(rated) / len(rated), 2)  # round to 2 decimal places
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

