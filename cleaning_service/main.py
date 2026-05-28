import time
from datetime import datetime
from cassandra.cluster import Cluster
from cassandra.cluster import NoHostAvailable


def load_properties(filepath):
    props = {}
    with open(filepath, "r", encoding="latin-1") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.split("=")
                props[key.strip()] = value.strip()
    return props


config = load_properties("config.properties")
TTL_MODE = config.get("ttl_mode", "accessed")
TTL_VALUE_MS = int(config.get("ttl_value_seconds", "60")) * 1000
INTERVAL = int(config.get("cleanup_interval_seconds", "10"))

print(f"[CLEANING] Uruchomiono serwis czyszczenia danych (Cleaning Service).")
print(f"[CLEANING] Tryb: {TTL_MODE}, Limit TTL: {config.get('ttl_value_seconds')}s, Interwał: {INTERVAL}s")

session = None
for attempt in range(15):
    try:
        cluster = Cluster(['cassandra-node1'], port=9042)
        session = cluster.connect()
        session.set_keyspace('link_shortener')
        print("[CLEANING] Połączono z klastrem Cassandra.")
        break
    except NoHostAvailable:
        print("[CLEANING] Oczekiwanie na gotowość klastra bazy danych...")
        time.sleep(5)

if not session:
    exit(1)

delete_stmt = session.prepare("DELETE FROM short_links WHERE short_id = ?")

while True:
    print("\n[CLEANING] Rozpoczynanie cyklicznego skanowania klastra NoSQL...")
    try:
        rows = session.execute("SELECT short_id, created_at, last_accessed_at FROM short_links")
        now_ms = int(time.time() * 1000)
        deleted_count = 0

        for row in rows:
            dt_object = row.created_at if TTL_MODE == "created" else row.last_accessed_at

            if dt_object is None:
                continue

            timestamp_to_check_ms = int(dt_object.timestamp() * 1000)

            age_ms = now_ms - timestamp_to_check_ms

            if age_ms > TTL_VALUE_MS:
                print(
                    f"[CLEANING][USUWANIE] Wpis ID: {row.short_id} przekroczył dozwolony TTL. (Wiek: {age_ms // 1000}s). Usuwanie z klastra...")
                session.execute(delete_stmt, (row.short_id,))
                deleted_count += 1
            else:
                print(f"[CLEANING][OK] Wpis ID: {row.short_id} jest aktualny. (Wiek: {age_ms // 1000}s)")

        print(f"[CLEANING] Zakończono skanowanie. Usunięto przeterminowanych wpisów: {deleted_count}")

    except Exception as e:
        print(f"[CLEANING][BŁĄD] Wystąpił problem podczas czyszczenia danych: {str(e)}")

    time.sleep(INTERVAL)