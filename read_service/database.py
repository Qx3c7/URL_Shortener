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

select_stmt = None
update_access_stmt = None

for attempt in range(10):
    try:
        session.set_keyspace('link_shortener')
        select_stmt = session.prepare("SELECT original_url FROM short_links WHERE short_id = ?")
        update_access_stmt = session.prepare("UPDATE short_links SET last_accessed_at = ? WHERE short_id = ?")
        break
    except InvalidRequest:
        time.sleep(3)

def get_url(short_id: str):
    result = session.execute(select_stmt, (short_id,)).one()
    if result:
        now = int(time.time() * 1000)
        session.execute(update_access_stmt, (now, short_id))
        return result.original_url
    return None