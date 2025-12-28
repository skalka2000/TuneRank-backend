from sqlalchemy.orm import Session
import app.models, app.schemas

def create_album(db: Session, album: app.schemas.AlbumCreate):
    print("Album: ", album)
    db_album = app.models.Album(**album.dict())  # Unpack validated schema into ORM
    print(db_album)
    db.commit()
    db.refresh(db_album)
    return db_album

def get_albums(db: Session):
    return db.query(app.models.Album).all()

