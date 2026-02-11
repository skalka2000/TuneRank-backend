from sqlalchemy.orm import Session
from sqlalchemy import func
import app.models, app.schemas
from typing import Optional, List

def create_album(db: Session, album: app.schemas.AlbumCreate, user_id: int):

    existing = db.query(app.models.Album).filter(
        app.models.Album.user_id == user_id,
        func.lower(app.models.Album.title) == album.title.strip().lower(),
        func.lower(app.models.Album.artist) == album.artist.strip().lower()
    ).first()

    if existing:
        raise ValueError("Album already exists")

    album_data = album.dict(exclude={"songs"})

    db_album = app.models.Album(
        **album_data,
        user_id=user_id
    )

    if album.songs:
        for song in album.songs:
            db_song = app.models.Song(
                **song.dict(),
                user_id=user_id
            )
            db_album.songs.append(db_song)

    db.add(db_album)
    db.commit()
    db.refresh(db_album)
    return db_album

def get_albums(db: Session, user_id: int):
    return db.query(app.models.Album).filter(
        app.models.Album.user_id == user_id
    ).all()


def get_album_by_id(db: Session, album_id: int, user_id: int):
    return db.query(app.models.Album).filter(
        app.models.Album.id == album_id,
        app.models.Album.user_id == user_id
    ).first()

def get_songs_by_album(db: Session, album_id: int, user_id: int):

    album = get_album_by_id(db, album_id, user_id)
    if not album:
        raise ValueError("Album does not exist")

    return db.query(app.models.Song).filter(
        app.models.Song.album_id == album_id,
        app.models.Song.user_id == user_id
    ).all()

def get_song_by_id(db: Session, song_id: int, user_id: int):
    return db.query(app.models.Song).filter(
        app.models.Song.id == song_id,
        app.models.Song.user_id == user_id
    ).first()

def create_song(db: Session, album_id: int, song: app.schemas.SongCreate, user_id: int):

    album = get_album_by_id(db, album_id, user_id)
    if not album:
        raise ValueError("Album does not exist")

    existing_song = db.query(app.models.Song).filter(
        app.models.Song.album_id == album_id,
        app.models.Song.user_id == user_id,
        func.lower(app.models.Song.title) == song.title.strip().lower()
    ).first()

    if existing_song:
        raise ValueError("Song already exists")

    db_song = app.models.Song(
        **song.dict(),
        album_id=album_id,
        user_id=user_id
    )

    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song

def delete_album(db: Session, album_id: int, user_id: int):

    album = get_album_by_id(db, album_id, user_id)

    if not album:
        raise ValueError("Album not found")

    db.delete(album)
    db.commit()

def delete_song(db: Session, song_id: int, user_id: int):

    song = db.query(app.models.Song).filter(
        app.models.Song.id == song_id,
        app.models.Song.user_id == user_id
    ).first()

    if not song:
        raise ValueError("Song not found")

    db.delete(song)
    db.commit()

def get_album_by_title_and_artist(db: Session, title: str, artist: str, user_id: int):
    return db.query(app.models.Album).filter(
        app.models.Album.user_id == user_id,
        func.lower(app.models.Album.title) == title.strip().lower(),
        func.lower(app.models.Album.artist) == artist.strip().lower()
    ).first()

def get_song_by_title_and_album(db: Session, album_id: int, title: str, user_id: int):
    return db.query(app.models.Song).filter(
        app.models.Song.album_id == album_id,
        app.models.Song.user_id == user_id,
        func.lower(app.models.Song.title) == title.strip().lower()
    ).first()


def get_filtered_songs(
    db: Session,
    user_id: int,
    artist_names: Optional[List[str]] = None,
    album_ids: Optional[List[int]] = None,
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None,
    title_contains: Optional[str] = None,
    sort_by=None,
    order="asc",
    is_interlude: Optional[bool] = None,
):

    query = db.query(app.models.Song).join(app.models.Album).filter(
        app.models.Song.user_id == user_id
    )

    if artist_names:
        query = query.filter(func.lower(app.models.Album.artist).in_(
            [name.strip().lower() for name in artist_names]
        ))

    if album_ids:
        query = query.filter(
            app.models.Song.album_id.in_(album_ids),
            app.models.Album.user_id == user_id
        )

    if min_rating is not None:
        query = query.filter(app.models.Song.rating >= min_rating)

    if max_rating is not None:
        query = query.filter(app.models.Song.rating <= max_rating)

    if title_contains:
        query = query.filter(app.models.Song.title.ilike(f"%{title_contains}%"))

    if is_interlude is not None:
        query = query.filter(app.models.Song.is_interlude == is_interlude)

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
    user_id: int,
    artist_names=None,
    min_rating=None,
    max_rating=None,
    title_contains=None,
    sort_by=None,
    order="asc"
):
    query = db.query(app.models.Album).filter(
        app.models.Album.user_id == user_id
    )

    if artist_names:
        query = query.filter(
            func.lower(app.models.Album.artist).in_(
                [name.strip().lower() for name in artist_names]
            )
        )

    if min_rating is not None:
        query = query.filter(app.models.Album.rating >= min_rating)

    if max_rating is not None:
        query = query.filter(app.models.Album.rating <= max_rating)

    if title_contains:
        query = query.filter(app.models.Album.title.ilike(f"%{title_contains}%"))

    # Sorting
    if sort_by:
        sort_column_map = {
            "rating": app.models.Album.rating,
            "title": app.models.Album.title,
            "artist": app.models.Album.artist,
            "year": app.models.Album.year
        }

        column = sort_column_map.get(sort_by)
        if column is not None:
            order_func = {
                "asc": column.asc(),
                "desc": column.desc()
            }.get(order.lower(), column.asc())

            query = query.order_by(order_func)

    return query.all()


def update_album(db: Session, album_id: int, updates: app.schemas.AlbumUpdate, user_id: int):

    album = db.query(app.models.Album).filter(
        app.models.Album.id == album_id,
        app.models.Album.user_id == user_id
    ).first()

    if not album:
        raise ValueError("Album not found")

    for field, value in updates.dict(exclude_unset=True).items():
        setattr(album, field, value)

    db.commit()
    db.refresh(album)
    return album

def update_song(db: Session, song_id: int, updates: app.schemas.SongUpdate, user_id: int):

    song = db.query(app.models.Song).filter(
        app.models.Song.id == song_id,
        app.models.Song.user_id == user_id
    ).first()

    if not song:
        raise ValueError("Song not found")

    for field, value in updates.dict(exclude_unset=True).items():
        setattr(song, field, value)

    db.commit()
    db.refresh(song)
    return song

def get_user_settings(db: Session, user_id: int):
    return db.query(app.models.UserSettings).filter(
        app.models.UserSettings.user_id == user_id
    ).first()

def create_user_settings(db: Session, user_id: int, settings: app.schemas.UserSettingsCreate):

    db_settings = app.models.UserSettings(
        user_id=user_id,
        **settings.dict()
    )

    db.add(db_settings)
    db.commit()
    db.refresh(db_settings)
    return db_settings

def update_user_settings(db: Session, user_id: int, settings: app.schemas.UserSettingsCreate):

    db_settings = get_user_settings(db, user_id)

    if not db_settings:
        return create_user_settings(db, user_id, settings)

    for field, value in settings.dict().items():
        setattr(db_settings, field, value)

    db.commit()
    db.refresh(db_settings)

    return db_settings
