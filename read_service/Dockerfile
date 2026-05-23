FROM python:3.11-slim

# Ustawienie katalogu roboczego wewnątrz kontenera
WORKDIR /app

# Kopiujemy listę bibliotek
COPY requirements.txt .

# Instalacja zależności (w tym cassandra-driver z nowego requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy pliki kodu lokalnego do kontenera
COPY database.py .
COPY main.py .

# Komenda startowa uruchamiająca serwer FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]