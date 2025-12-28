from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class Album(Base):
    __tablename__ = "albums"  # SQL table name

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    year = Column(Integer)
    rating = Column(Float)
