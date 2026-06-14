# Rozproszony System Skracania Linków

Projekt przedstawia architekturę rozproszoną aplikacji do skracania adresów URL, podzieloną na dwa niezależne serwisy współpracujące z klastrem bazy danych Cassandra.

## Architektura systemu

Aplikacja składa się z następujących komponentów:

*   **Write Service (Port 8000)**: Odpowiada za przyjmowanie długich adresów URL, generowanie unikalnych identyfikatorów Base62 oraz zapisywanie danych w bazie.
*   **Read Service (Port 8001)**: Obsługuje żądania przekierowań, sprawdza ważność linku i usuwa wygasłe wpisy.
*   **Cleaning Service**: Autonomiczny serwis działający w tle, który cyklicznie skanuje bazę danych i usuwa przeterminowane rekordy na podstawie zewnętrznego pliku konfiguracyjnego config.properties.
*   **Klaster Apache Cassandra (Port 9042)**: Składa się z dwóch niezależnych węzłów (cassandra-node1 jako Seed Node oraz cassandra-node2) zapewniających wysoką dostępność, odporność na awarie (Fault Tolerance) oraz replikację danych na poziomie klastra.
* **RabbitMQ (Porty 5672, 15672)**: Broker wiadomości pośredniczący w wymianie informacji o incydentach bezpieczeństwa. Przechowuje alerty JSON w trwałej kolejce `banned_urls_alerts`. Posiada wbudowany panel administracyjny .

## Wymagania

*   Docker Desktop
*   Docker Compose

## Szybki start

1.  Sklonuj repozytorium.
2.  W głównym folderze projektu uruchom komendę:
    ```powershell
    docker-compose up --build -d
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


### 3. Panel administracyjny RabbitMQ

Broker wiadomości udostępnia graficzny interfejs do monitorowania kolejek i przesyłanych komunikatów.

* Adres: http://localhost:15672

* Domyślny użytkownik: guest

* Domyślne hasło: guest

---

## Koniguracja Cleaning Service
Usługa czyszcząca pobiera parametry sterujące czasem życia linków z pliku cleaning_service/config.properties. Możliwa jest konfiugrcja nastepujących właściwości:
* **ttl_mode** Tryb obliczania wieku wpisu.
  * created - usuwa wpisy na podstawie czasu ich utworzenia
  * acessed - usuwa wpisy na podstawie czasu ich ostatniego użycia
* **ttl_value_seconds** Czas ważności linku wyrażony w sekundach.
* **cleanup_interval_seconds** Interwał uruchamiania pętli skanjącej baze danych 

---

## Logika biznesowa i parametry
Algorytm ID: Identyfikatory są generowane na podstawie fragmentów UUID konwertowanych do systemu Base62.  

System Bezpieczeństwa (Słowa Zakazane):

Aplikacja posiada wbudowany mechanizm filtrowania linków wejściowych pod kątem bezpieczeństwa na podstawie zdefiniowanej listy słów kluczowych (malware, phishing, casino, gamble).
W przypadku wykrycia zakazanego słowa w polu target_url:

* Żądanie zostaje natychmiast przerwane bez zapisu w bazie danych Cassandra.

* Zwracany jest kod błędu 400 Bad Request.

* Informacja o incydencie zostaje wysłana do systemu kolejkowego RabbitMQ jako obiekt JSON o strukturze:
```JSON
{
  "timestamp": "ISO-8601-TIMESTAMP",
  "alert_type": "BANNED_WORD_DETECTED",
  "detected_word": "nazwa_słowa",
  "attempted_url": "pełny_zablokowany_url"
}
```


Obsługa błędów:
    
* 404 Not Found: Gdy identyfikator nie istnieje w bazie danych.  

* 500 Internal Server Error: W przypadku problemów z komunikacją wewnątrz sieci rozproszonej.

* 400 Bad Request: Gdy przesłany adres URL zawiera słowo uznane za niebezpieczne.

Przekierowanie: Wykorzystywany jest status HTTP 307 (Temporary Redirect).