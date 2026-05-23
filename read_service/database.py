import time
from cassandra.cluster import Cluster
from cassandra.cluster import NoHostAvailable
from cassandra import InvalidRequest

session = None

for attempt in range(15):
    try:
        print(f"[Cassandra-Read] Próba połączenia z klastrem ({attempt + 1}/15)...")
        cluster = Cluster(['cassandra-node1'], port=9042)
        session = cluster.connect()
        print("[Cassandra-Read] Połączono pomyślnie z węzłem bazy danych!")
        break
    except NoHostAvailable:
        print("[Cassandra-Read] Port 9042 nie jest jeszcze gotowy. Oczekiwanie 3 sekundy...")
        time.sleep(3)

if not session:
    raise RuntimeError("Nie można nawiązać połączenia z klastrem Cassandra po 15 próbach.")

select_stmt = None
for attempt in range(10):
    try:
        session.set_keyspace('link_shortener')
        select_stmt = session.prepare("SELECT original_url FROM short_links WHERE short_id = ?")
        print("[Cassandra-Read] Serwis odczytu pomyślnie podpiął się pod tabelę short_links.")
        break
    except InvalidRequest:
        print(f"[Cassandra-Read] Tabela lub keyspace jeszcze nie istnieje, próba ({attempt + 1}/10). Oczekiwanie 3 sekundy...")
        time.sleep(3)

if not select_stmt:
    raise RuntimeError("Serwis odczytu nie doczekał się na utworzenie struktur bazy danych.")

def get_url(short_id: str):
    result = session.execute(select_stmt, (short_id,)).one()
    if result:
        return result.original_url
    return None