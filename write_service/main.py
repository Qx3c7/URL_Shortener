import string
import uuid
import time
from fastapi import FastAPI, Depends
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from database import URLModel, get_db, engine, Base 

app = FastAPI(title="URL Shortener - Write Service")
Base.metadata.create_all(bind=engine)

def generate_short_id() -> str:
    unique_id = uuid.uuid4().int >> 96
    alphabet = string.digits + string.ascii_letters
    arr = []
    base = len(alphabet)
    while unique_id:
        unique_id, rem = divmod(unique_id, base)
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)

class ShortenRequest(BaseModel):
    url: HttpUrl

@app.post("/shorten")
def shorten_url(payload: ShortenRequest, db: Session = Depends(get_db)):
    short_id = generate_short_id()
    
    # Czas życia linku: 300 sekund
    expiry_time = time.time() + 300

    db_url = URLModel(
        short_id=short_id,
        original_url=str(payload.url),
        expires_at=expiry_time
    )
    
    db.add(db_url)
    db.commit()

    return {
        "short_url": f"http://localhost:8001/{short_id}",
        "expires_at": expiry_time
    }
