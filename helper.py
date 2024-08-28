import sqlite3
import pandas as pd

DB0 = "keylog.db"
DB1 = "keylog1.db"
DB2 = "keylog2.db"
DB3 = "keylog3.db"


# from table 'keylog' in DB 1,
# move copy all rows to DB0.
run = False
df = None
if run:
    for DB in [DB2, DB3]:
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM keylog")
            rows = c.fetchall()
            df = pd.DataFrame(rows)

        with sqlite3.connect(DB0) as conn:
            c = conn.cursor()
            for index, row in df.iterrows():
                c.execute('''INSERT INTO keylog (key, timestamp, application, window_title, key_hold_duration) VALUES (?, ?, ?, ?, ?)''',
                          (row[1], row[2], row[3], row[4], row[5]))
            conn.commit()
