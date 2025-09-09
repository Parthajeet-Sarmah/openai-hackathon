import sqlite3

class EventFetcher:
    def __init__(self, db_path):
        self.db_path = db_path
        self.last_timestamp = 0  # track latest fetched timestamp

    def fetch_recent_events(self, event_type=None, limit=100):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("SELECT MAX(timestamp) FROM events")
        c = cur.fetchone()[0]
        max_timestamp = c if c else 0

        print(self.last_timestamp, max_timestamp, self.last_timestamp == max_timestamp)

        if self.last_timestamp >= max_timestamp:
            self.last_timestamp = max_timestamp
            conn.close()
            return []
        
        self.last_timestamp = max_timestamp

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
