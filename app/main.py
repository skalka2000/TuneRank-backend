from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas, crud
from app.database import SessionLocal, engine
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware



models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Hello, world"}

@app.post("/albums", response_model=schemas.Album)
def create_album(album: schemas.AlbumCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_album(db=db, album=album)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/albums", response_model=List[schemas.Album])
def get_albums_filtered(
    artist_names: Optional[List[str]] = Query(default=None),
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None,
    title_contains: Optional[str] = None,
    sort_by: Optional[str] = Query(default=None),
    order: str = Query(default="asc"),
    power: float = Query(default=1.0),
    db: Session = Depends(get_db)
):
    albums = crud.get_filtered_albums(
        db,
        artist_names=artist_names,
        min_rating=min_rating,
        max_rating=max_rating,
        title_contains=title_contains,
        sort_by=sort_by,
        order=order
    )

    for album in albums:
        album._average_power = power

    return albums

@app.get("/albums/{album_id}", response_model=schemas.Album)
def read_album(album_id: int, power: float = Query(1.0), db: Session = Depends(get_db)):
    album = crud.get_album_by_id(db, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    album._average_power = power
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

@app.get("/songs", response_model=List[schemas.Song])
def get_songs_filtered(
    artist_names: Optional[List[str]] = Query(default=None),
    album_ids: Optional[List[int]] = Query(default=None),
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None,
    title_contains: Optional[str] = None,
    sort_by: Optional[str] = Query(default=None),
    order: str = Query(default="asc"),
    db: Session = Depends(get_db),
    is_interlude: Optional[bool] = Query(default=None),

):
    return crud.get_filtered_songs(
        db,
        artist_names=artist_names,
        album_ids=album_ids,
        min_rating=min_rating,
        max_rating=max_rating,
        title_contains=title_contains,
        sort_by=sort_by,
        order = order,
        is_interlude=is_interlude
    )

@app.patch("/albums/{album_id}", response_model=schemas.Album)
def update_album(album_id: int, updates: schemas.AlbumUpdate, db: Session = Depends(get_db)):
    try:
        return crud.update_album(db, album_id, updates)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.patch("/songs/{song_id}", response_model=schemas.Song)
def update_song(song_id: int, updates: schemas.SongUpdate, db: Session = Depends(get_db)):
    try:
        return crud.update_song(db, song_id, updates)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
