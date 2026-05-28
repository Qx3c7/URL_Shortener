import time
from cassandra.cluster import Cluster
from cassandra.cluster import NoHostAvailable
from cassandra import InvalidRequest

session = None
for attempt in range(15):
    try:
        cluster = Cluster(['cassandra-node1'], port=9042)
        session = cluster.connect()
        break
    except NoHostAvailable:
        time.sleep(3)

if not session:
    raise RuntimeError("Brak połączenia z Cassandra.")

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
                original_url text,
                created_at timestamp,
                last_accessed_at timestamp
            );
        """)
        break
    except InvalidRequest:
        time.sleep(2)

insert_stmt = session.prepare(
    "INSERT INTO short_links (short_id, original_url, created_at, last_accessed_at) VALUES (?, ?, ?, ?)")


def save_url(short_id: str, original_url: str):
    now = int(time.time() * 1000)
    session.execute(insert_stmt, (short_id, original_url, now, now))
    print(f"[Cassandra] Zapisano: {short_id} -> {original_url}")