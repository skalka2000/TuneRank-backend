from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
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

@app.post("/albums", response_model=schemas.Album)
def create_album(album: schemas.AlbumCreate, db: Session = Depends(get_db)):
    return crud.create_album(db=db, album=album)

@app.get("/albums", response_model=List[schemas.Album])
def read_albums(db: Session = Depends(get_db)):
    return crud.get_albums(db)
