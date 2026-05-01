FROM python:3.11-slim

# Ustawienie katalogu roboczego wewnątrz kontenera
WORKDIR /app

# Kopiujemy listę bibliotek z głównego folderu
COPY requirements.txt .

# Instalacja zależności
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy pliki kodu do kontenera
COPY database.py .
COPY main.py .

# Komenda startowa
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]