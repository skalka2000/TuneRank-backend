from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas, crud
from app.database import SessionLocal, engine
from typing import List


models.Base.metadata.create_all(bind=engine)


app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Hello, world"}

@app.get("/albums/by-artist", response_model=List[schemas.Album])
def get_albums_by_artist(name: str, db: Session = Depends(get_db)):
    return crud.get_albums_by_artist(db, name)

@app.get("/songs/by-artist", response_model=List[schemas.Song])
def get_songs_by_artist(name: str, db: Session = Depends(get_db)):
    return crud.get_songs_by_artist(db, name)

@app.post("/albums", response_model=schemas.Album)
def create_album(album: schemas.AlbumCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_album(db=db, album=album)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/albums", response_model=List[schemas.Album])
def read_albums(db: Session = Depends(get_db)):
    return crud.get_albums(db)

@app.get("/albums/{album_id}", response_model=schemas.Album)
def read_album(album_id: int, db: Session = Depends(get_db)):
    album = crud.get_album_by_id(db, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    return album

@app.post("/albums/{album_id}/songs", response_model=schemas.Song)
def add_song_to_album(album_id: int, song: schemas.SongCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_song(db, album_id, song)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@app.get("/albums/{album_id}/songs", response_model=List[schemas.Song])
def get_songs(album_id: int, db: Session = Depends(get_db)):
    try:
        return crud.get_songs_by_album(db, album_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@app.get("/songs/{song_id}", response_model=schemas.Song)
def get_song(song_id: int, db: Session = Depends(get_db)):
    song = crud.get_song_by_id(db, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song

@app.delete("/albums/{album_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_album(album_id: int, db: Session = Depends(get_db)):
    try:
        crud.delete_album(db, album_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/songs/{song_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_song(song_id: int, db: Session = Depends(get_db)):
    try:
        crud.delete_song(db, song_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
