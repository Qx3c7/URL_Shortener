import time
from cassandra.cluster import Cluster
from cassandra.cluster import NoHostAvailable
from cassandra import InvalidRequest

session = None

for attempt in range(15):
    try:
        print(f"[Cassandra-Write] Próba połączenia z klastrem ({attempt + 1}/15)...")
        cluster = Cluster(['cassandra-node1'], port=9042)
        session = cluster.connect()
        print("[Cassandra-Write] Połączono pomyślnie z węzłem bazy danych!")
        break
    except NoHostAvailable:
        print("[Cassandra-Write] Port 9042 nie jest jeszcze gotowy. Oczekiwanie 3 sekundy...")
        time.sleep(3)

if not session:
    raise RuntimeError("Nie można nawiązać połączenia z klastrem Cassandra po 15 próbach.")

for attempt in range(10):
    try:
        session.execute("""
            CREATE KEYSPACE IF NOT EXISTS link_shortener
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 2};
        """)
        session.set_keyspace('link_shortener')

        session.execute("""
            CREATE TABLE IF NOT EXISTS short_links (
                short_id text PRIMARY KEY,
                original_url text
            );
        """)
        print("[Cassandra-Write] Struktura bazy danych została pomyślnie przygotowana.")
        break
    except InvalidRequest as e:
        print(f"[Cassandra-Write] Klaster synchronizuje schemat, próba ({attempt + 1}/10). Oczekiwanie 2 sekundy...")
        time.sleep(2)

insert_stmt = session.prepare("INSERT INTO short_links (short_id, original_url) VALUES (?, ?)")


def save_url(short_id: str, original_url: str):
    session.execute(insert_stmt, (short_id, original_url))
    print(f"[Cassandra] Zapisano: {short_id} -> {original_url}")