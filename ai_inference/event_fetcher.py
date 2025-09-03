import sqlite3

def fetch_recent_events(db_path, event_type=None, limit=100):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    q = "SELECT timestamp, source, event, data FROM events"
    params = []
    if event_type:
        q += " WHERE event = ?"
        params.append(event_type)
    q += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    cur.execute(q, params)
    rows = cur.fetchall()
    conn.close()
    return rows
