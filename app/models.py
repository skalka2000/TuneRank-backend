from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils import calculate_weighted_average, apply_logistic_normalization
import math

album_genres = Table(
    "album_genres",
    Base.metadata,
    Column("album_id", Integer, ForeignKey("albums.id"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id"), primary_key=True),
)

class Album(Base):
    __tablename__ = "albums"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)  # ADDED
    title = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    year = Column(Integer, nullable=True)
    rating = Column(Float, nullable=True)

    user = relationship("User", back_populates="albums")
    songs = relationship("Song", back_populates="album", cascade="all, delete-orphan")
    genres = relationship(
        "Genre",
        secondary=album_genres,
        back_populates="albums"
    )


    @property
    def average_rating(self):
        if not self.songs:
            return None

        power = getattr(self, "_average_power", 1.0)
        greatness_threshold = getattr(self, "_greatness_threshold", 8.0)
        scaling_factor = getattr(self, "_scaling_factor", 0.3)
        steep_factor = getattr(self, "_steep_factor", 3)
        interlude_weight = getattr(self, "_interlude_weight", 0.5)
        epic_weight = getattr(self, "_epic_weight", 2.0)

        weighted_average = calculate_weighted_average(self.songs, power, interlude_weight, epic_weight)

        if weighted_average is None:
            return None

        return round(
            apply_logistic_normalization(
                weighted_average,
                greatness_threshold,
                scaling_factor,
                steep_factor
            ),
            3
        )

    @property
    def overall_rating(self):
        average_rating_weight = getattr(self, "_average_rating_weight", 0.5)
        if self.rating is not None:
            if self.average_rating is not None:
                return math.floor(
                    (self.rating * (1 - average_rating_weight) + self.average_rating * average_rating_weight) * 100
                ) / 100
            else:
                return self.rating
        return None


class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)  # ADDED
    album_id = Column(Integer, ForeignKey("albums.id", ondelete="CASCADE"))
    title = Column(String, nullable=False)
    track_number = Column(Integer)
    rating = Column(Float)
    song_type = Column(String, nullable=False, default="song")

    album = relationship("Album", back_populates="songs")
    user = relationship("User", back_populates="songs")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    albums = relationship("Album", back_populates="user", cascade="all, delete-orphan")
    songs = relationship("Song", back_populates="user", cascade="all, delete-orphan")

class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    average_power = Column(Float, default=1.0)
    greatness_threshold = Column(Float, default=8.0)
    scaling_factor = Column(Float, default=0.3)
    steep_factor = Column(Float, default=3.0)
    average_rating_weight = Column(Float, default=0.5)
    interlude_weight = Column(Float, default=0.5)
    epic_weight = Column(Float, default=2.0)

    user = relationship("User")

class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    albums = relationship(
        "Album",
        secondary="album_genres",
        back_populates="genres"
    )

