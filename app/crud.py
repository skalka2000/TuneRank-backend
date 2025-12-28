from sqlalchemy.orm import Session
import app.models, app.schemas

def get_album_by_title_and_artist(db: Session, title: str, artist: str):
    return db.query(app.models.Album).filter(
        app.models.Album.title == title,
        app.models.Album.artist == artist
    ).first()

def create_album(db: Session, album: app.schemas.AlbumCreate):
    existing = get_album_by_title_and_artist(db, album.title, album.artist)
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

