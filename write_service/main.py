from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import string
import random
from database import save_url

app = FastAPI(title="Link Shortener - Write Service (NoSQL Cassandra)")


class URLRequest(BaseModel):
    target_url: HttpUrl


def generate_short_id() -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))


@app.post("/shorten")
def shorten_url(request: URLRequest):
    short_id = generate_short_id()
    original_url = str(request.target_url)

    try:
        save_url(short_id, original_url)
        return {
            "short_id": short_id,
            "short_url": f"http://localhost:8001/{short_id}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Błąd podczas zapisu w rozproszonej bazie danych: {str(e)}"
        )