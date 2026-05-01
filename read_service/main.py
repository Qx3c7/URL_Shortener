import time
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import URLModel, get_db

app = FastAPI(title="URL Shortener - Read Service")

@app.get("/{short_id}")
def redirect_to_url(short_id: str, db: Session = Depends(get_db)):
    entry = db.query(URLModel).filter(URLModel.short_id == short_id).first()

    if not entry:
        raise HTTPException(status_code=404, detail="URL nie został znaleziony")

    if time.time() > entry.expires_at:
        db.delete(entry)
        db.commit()
        raise HTTPException(status_code=410, detail="Ten krótki URL już wygasł")

    return RedirectResponse(url=entry.original_url)
