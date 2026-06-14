import json
import string
import random
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import pika
from database import save_url

app = FastAPI(title="Link Shortener - Write Service (NoSQL Cassandra)")

BANNED_WORDS = ["malware", "phishing", "casino", "gamble"]


class URLRequest(BaseModel):
    target_url: HttpUrl


def generate_short_id() -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))


def send_to_queue(banned_word: str, url: str):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()
        channel.queue_declare(queue='banned_urls_alerts', durable=True)
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "alert_type": "BANNED_WORD_DETECTED",
            "detected_word": banned_word,
            "attempted_url": url
        }
        channel.basic_publish(
            exchange='',
            routing_key='banned_urls_alerts',
            body=json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
    except Exception as e:
        print(f"Error sending to RabbitMQ: {str(e)}")


@app.post("/shorten")
def shorten_url(request: URLRequest):
    original_url = str(request.target_url)

    for word in BANNED_WORDS:
        if word in original_url.lower():
            send_to_queue(word, original_url)
            raise HTTPException(
                status_code=400,
                detail=f"URL contains a banned word: {word}"
            )

    short_id = generate_short_id()
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