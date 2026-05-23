from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from database import get_url

app = FastAPI(title="Link Shortener - Read Service (NoSQL Cassandra)")


@app.get("/{short_id}")
def redirect_to_target(short_id: str):
    try:
        original_url = get_url(short_id)

        if original_url:
            return RedirectResponse(url=original_url, status_code=307)

        raise HTTPException(
            status_code=404,
            detail="Podany skrót kodu nie istnieje w klastrze NoSQL"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Błąd komunikacji z klastrem rozproszonym: {str(e)}"
        )