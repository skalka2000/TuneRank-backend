from sqlalchemy.orm import Session
from sqlalchemy import func
import app.models, app.schemas

def get_album_by_title_and_artist(db: Session, title: str, artist: str):
    return db.query(app.models.Album).filter(
        app.models.Album.title == title,
        app.models.Album.artist == artist
    ).first()

def create_album(db: Session, album: app.schemas.AlbumCreate):
    existing = db.query(app.models.Album).filter(
        func.lower(app.models.Album.title) == album.title.strip().lower(),
        func.lower(app.models.Album.artist) == album.artist.strip().lower()
    ).first()
    if existing:
        raise ValueError("Album already exists")
    db_album = app.models.Album(**album.dict())
    db.add(db_album)
    db.commit()
    db.refresh(db_album)
    return db_album

def get_albums(db: Session):
    return db.query(app.models.Album).all()

def get_album_by_id(db: Session, album_id: int):
    return db.query(app.models.Album).filter(app.models.Album.id == album_id).first()

def get_songs_by_album(db: Session, album_id: int):
    album = db.query(app.models.Album).filter(app.models.Album.id == album_id).first()
    if not album:
        raise ValueError("Album does not exist")

    return db.query(app.models.Song).filter(app.models.Song.album_id == album_id).all()

def get_song_by_title_and_album(db: Session, album_id: int, title: str):
    return db.query(app.models.Song).filter(
        app.models.Song.album_id == album_id,
        func.lower(app.models.Song.title) == title.strip().lower()
    ).first()


def create_song(db: Session, album_id: int, song: app.schemas.SongCreate):
    album = db.query(app.models.Album).filter(app.models.Album.id == album_id).first()
    if not album:
        raise ValueError("Album does not exist")
    existing_song = get_song_by_title_and_album(db, album_id, song.title)
    if existing_song:
        raise ValueError("Song already exists on this album")
    db_song = app.models.Song(**song.dict(), album_id=album_id)
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song

def delete_album(db: Session, album_id: int):
    album = db.query(app.models.Album).filter(app.models.Album.id == album_id).first()
    if not album:
        raise ValueError("Album not found")
    db.delete(album)
    db.commit()
