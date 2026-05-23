# Rozproszony System Skracania Linków

Projekt przedstawia architekturę rozproszoną aplikacji do skracania adresów URL, podzieloną na dwa niezależne serwisy współpracujące z klastrem bazy danych Cassandra.

## Architektura systemu

Aplikacja składa się z następujących komponentów:

*   **Write Service (Port 8000)**: Odpowiada za przyjmowanie długich adresów URL, generowanie unikalnych identyfikatorów Base62 oraz zapisywanie danych w bazie.
*   **Read Service (Port 8001)**: Obsługuje żądania przekierowań, sprawdza ważność linku i usuwa wygasłe wpisy.
*   **Klaster Apache Cassandra (Port 9042)**: Składa się z dwóch niezależnych węzłów (cassandra-node1 jako Seed Node oraz cassandra-node2) zapewniających wysoką dostępność, odporność na awarie (Fault Tolerance) oraz replikację danych na poziomie klastra.

## Wymagania

*   Docker Desktop
*   Docker Compose

## Szybki start

1.  Sklonuj repozytorium.
2.  W głównym folderze projektu uruchom komendę:
    ```powershell
    docker-compose up --build
    ```
3.  Poczekaj, aż wszystkie kontenery zgłoszą status `Healthy` lub `Started`. 

---

## Instrukcja obsługi

### 1. Generowanie krótkiego linku
Użyj **Write Service** działającego na porcie 8000, aby utworzyć nowy skrót.

**Zapytanie (PowerShell):**
```powershell
Invoke-RestMethod -Uri http://localhost:8000/shorten -Method Post -ContentType "application/json" -Body '{"url": "[https://www.google.com](https://www.google.com)"}'
```
**Zapytanie (cURL):**
```Bash
curl -X POST http://localhost:8000/shorten -H "Content-Type: application/json" -d '{"url": "[https://www.google.com](https://www.google.com)"}'
```
### 2. Korzystanie z przekierowania

Użyj **Read Service** działającego na porcie 8001, aby skorzystać z wygenerowanego linku.

Adres: http://localhost:8001/{identyfikator}

---

## Logika biznesowa i parametry
Algorytm ID: Identyfikatory są generowane na podstawie fragmentów UUID konwertowanych do systemu Base62.  

Obsługa błędów:
    
* 404 Not Found: Gdy identyfikator nie istnieje w bazie danych.  

* 500 Internal Server Error: W przypadku problemów z komunikacją wewnątrz sieci rozproszonej.

Przekierowanie: Wykorzystywany jest status HTTP 307 (Temporary Redirect).
