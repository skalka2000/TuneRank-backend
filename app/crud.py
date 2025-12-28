from sqlalchemy.orm import Session
from sqlalchemy import func
import app.models, app.schemas
from typing import Optional, List

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

def get_song_by_id(db: Session, song_id: int):
    return db.query(app.models.Song).filter(app.models.Song.id == song_id).first()

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

def delete_song(db: Session, song_id: int):
    song = db.query(app.models.Song).filter(app.models.Song.id == song_id).first()
    if not song:
        raise ValueError("Song not found")
    db.delete(song)
    db.commit()

def get_album_by_title_and_artist(db: Session, title: str, artist: str):
    return db.query(app.models.Album).filter(
        app.models.Album.title == title,
        app.models.Album.artist == artist
    ).first()

def get_song_by_title_and_album(db: Session, album_id: int, title: str):
    return db.query(app.models.Song).filter(
        app.models.Song.album_id == album_id,
        func.lower(app.models.Song.title) == title.strip().lower()
    ).first()

def get_filtered_songs(
    db: Session,
    artist_names: Optional[List[str]] = None,
    album_ids: Optional[List[int]] = None,
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None,
    title_contains: Optional[str] = None,
    sort_by = None,
    order = "asc",
):
    query = db.query(app.models.Song).join(app.models.Album)

    if artist_names:
        query = query.filter(func.lower(app.models.Album.artist).in_(
            [name.strip().lower() for name in artist_names]
        ))

    if album_ids:
        query = query.filter(app.models.Song.album_id.in_(album_ids))

    if min_rating is not None:
        query = query.filter(app.models.Song.rating >= min_rating)

    if max_rating is not None:
        query = query.filter(app.models.Song.rating <= max_rating)

    if title_contains:
        query = query.filter(app.models.Song.title.ilike(f"%{title_contains}%"))

    # Sorting logic
    if sort_by:
        order_func = {
            "asc": lambda col: col.asc(),
            "desc": lambda col: col.desc()
        }.get(order.lower(), lambda col: col.asc())

        sort_column_map = {
            "rating": app.models.Song.rating,
            "track_number": app.models.Song.track_number,
            "song_title": app.models.Song.title,
            "album_title": app.models.Album.title,
            "artist_name": app.models.Album.artist,
            "year": app.models.Album.year,
        }

        column = sort_column_map.get(sort_by)
        if column is not None:
            query = query.order_by(order_func(column))

    return query.all()

def get_filtered_albums(
    db: Session,
    artist_names=None,
    min_rating=None,
    max_rating=None,
    title_contains=None,
    sort_by=None,
    order="asc"
):
    query = db.query(app.models.Album)

    if artist_names:
        query = query.filter(func.lower(app.models.Album.artist).in_(
            [name.strip().lower() for name in artist_names]
        ))

    if min_rating is not None:
        query = query.filter(app.models.Album.rating >= min_rating)

    if max_rating is not None:
        query = query.filter(app.models.Album.rating <= max_rating)

    if title_contains:
        query = query.filter(app.models.Album.title.ilike(f"%{title_contains}%"))

    # Sorting logic
    if sort_by:
        order_func = {
            "asc": lambda col: col.asc(),
            "desc": lambda col: col.desc()
        }.get(order.lower(), lambda col: col.asc())

        sort_column_map = {
            "rating": app.models.Album.rating,
            "title": app.models.Album.title,
            "artist": app.models.Album.artist,
            "year": app.models.Album.year
        }

        column = sort_column_map.get(sort_by)
        if column is not None:
            query = query.order_by(order_func(column))

    return query.all()
