from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas, crud
from app.database import SessionLocal, engine
from typing import List, Optional, Literal
from fastapi.middleware.cors import CORSMiddleware
from app.utils import get_current_user_id



models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://tunerank-frontend.onrender.com", "https://tunerank-backend.onrender.com"],
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
def create_album(
    album: schemas.AlbumCreate, 
    db: Session = Depends(get_db), 
    user_id: int = Depends(get_current_user_id)
):
    try:
        return crud.create_album(db=db, album=album, user_id=user_id)
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
    genre_ids: Optional[List[int]] = Query(default=None),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    settings = crud.get_user_settings(db, user_id)

    if not settings:
        settings = crud.create_user_settings(
            db,
            user_id,
            schemas.UserSettingsCreate()
        )

    albums = crud.get_filtered_albums(
        db,
        user_id=user_id,
        artist_names=artist_names,
        min_rating=min_rating,
        max_rating=max_rating,
        title_contains=title_contains,
        sort_by=sort_by,
        order=order,
        genre_ids=genre_ids
    )

    for album in albums:
        album._average_power = settings.average_power
        album._greatness_threshold = settings.greatness_threshold
        album._scaling_factor = settings.scaling_factor
        album._steep_factor = settings.steep_factor
        album._average_rating_weight = settings.average_rating_weight
        album._interlude_weight = settings.interlude_weight
        album._epic_weight = settings.epic_weight
    return albums

@app.get("/albums/{album_id}", response_model=schemas.Album)
def read_album(
    album_id: int, 
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    settings = crud.get_user_settings(db, user_id)

    if not settings:
        settings = crud.create_user_settings(
            db,
            user_id,
            schemas.UserSettingsCreate()
        )    
    album = crud.get_album_by_id(db, album_id, user_id=user_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    
    album._average_power = settings.average_power
    album._greatness_threshold = settings.greatness_threshold
    album._scaling_factor = settings.scaling_factor
    album._steep_factor = settings.steep_factor
    album._average_rating_weight = settings.average_rating_weight 
    album._interlude_weight = settings.interlude_weight
    album._epic_weight = settings.epic_weight

    return album

@app.post("/albums/{album_id}/songs", response_model=schemas.Song)
def add_song_to_album(
    album_id: int,
    song: schemas.SongCreate, 
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)    
):
    try:
        return crud.create_song(db, album_id, song, user_id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@app.get("/albums/{album_id}/songs", response_model=List[schemas.Song])
def get_songs(
    album_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    try:
        return crud.get_songs_by_album(db, album_id, user_id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@app.get("/songs/{song_id}", response_model=schemas.Song)
def get_song(
    song_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    song = crud.get_song_by_id(db, song_id, user_id=user_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song

@app.delete("/albums/{album_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_album(
    album_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    try:
        crud.delete_album(db, album_id, user_id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/songs/{song_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_song(
    song_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    try:
        crud.delete_song(db, song_id, user_id=user_id)
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
    song_type: Optional[Literal["interlude", "song", "epic"]] = Query(default=None),
    user_id: int = Depends(get_current_user_id)
):
    return crud.get_filtered_songs(
        db,
        user_id=user_id,
        artist_names=artist_names,
        album_ids=album_ids,
        min_rating=min_rating,
        max_rating=max_rating,
        title_contains=title_contains,
        sort_by=sort_by,
        order=order,
        song_type=song_type,
    )

@app.patch("/albums/{album_id}", response_model=schemas.Album)
def update_album(
    album_id: int,
    updates: schemas.AlbumUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    try:
        return crud.update_album(db, album_id, updates, user_id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.patch("/songs/{song_id}", response_model=schemas.Song)
def update_song(
    song_id: int,
    updates: schemas.SongUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    try:
        return crud.update_song(db, song_id, updates, user_id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/user-settings", response_model=schemas.UserSettings)
def get_settings(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):

    settings = crud.get_user_settings(db, user_id)

    if not settings:
        # create defaults automatically
        settings = crud.create_user_settings(
            db,
            user_id,
            schemas.UserSettingsCreate()
        )

    return settings

@app.post("/user-settings", response_model=schemas.UserSettings)
def save_settings(
    settings: schemas.UserSettingsCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    return crud.update_user_settings(db, user_id, settings)


@app.get("/genres", response_model=List[schemas.Genre])
def get_genres(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    return crud.get_user_genres(db, user_id)

@app.post("/genres", response_model=schemas.Genre)
def create_genre(
    genre: schemas.GenreCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    return crud.create_genre(db, user_id, genre)

@app.delete("/genres/{genre_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_genre(
    genre_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    try:
        crud.delete_genre(db, genre_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/albums/{album_id}/genres/{genre_id}", response_model=schemas.Album)
def add_genre_to_album(
    album_id: int,
    genre_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    album = db.query(models.Album).filter(
        models.Album.id == album_id,
        models.Album.user_id == user_id
    ).first()

    if not album:
        raise HTTPException(status_code=404, detail="Album not found")

    genre = db.query(models.Genre).filter(
        models.Genre.id == genre_id,
        models.Genre.user_id == user_id
    ).first()

    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")

    if genre not in album.genres:
        album.genres.append(genre)
        db.commit()
        db.refresh(album)
    
    settings = crud.get_user_settings(db, user_id)

    if not settings:
        settings = crud.create_user_settings(
            db,
            user_id,
            schemas.UserSettingsCreate()
        )

    crud.apply_settings_to_album(album, settings)

    return album

@app.delete("/albums/{album_id}/genres/{genre_id}", response_model=schemas.Album)
def remove_genre_from_album(
    album_id: int,
    genre_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    album = db.query(models.Album).filter(
        models.Album.id == album_id,
        models.Album.user_id == user_id
    ).first()

    if not album:
        raise HTTPException(status_code=404, detail="Album not found")

    genre = db.query(models.Genre).filter(
        models.Genre.id == genre_id,
        models.Genre.user_id == user_id
    ).first()

    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")

    if genre in album.genres:
        album.genres.remove(genre)
        db.commit()
        db.refresh(album)

    settings = crud.get_user_settings(db, user_id)

    if not settings:
        settings = crud.create_user_settings(
            db,
            user_id,
            schemas.UserSettingsCreate()
        )  

    crud.apply_settings_to_album(album, settings)

    return album
