import imaplib
import email
from email.header import decode_header
from hashlib import sha256
import time
from datetime import datetime
import threading
import queue
from dotenv import dotenv_values
import sqlite3

# Gmail IMAP server settings
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993

EMAIL_USER = "tjraklovits@gmail.com"


EMAIL_PASS = dotenv_values(".env")["EMAIL_PASSWORD"]
PRINT = True
hashes = set()
# Gmail IMAP server settings

# Database file
DB_FILE = "keylog.db"
COUNT_FILE = "counter.txt"

# Queue for storing email metadata
email_queue = queue.Queue()


def connect_to_imap():
    """Connect to the Gmail IMAP server."""
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(EMAIL_USER, EMAIL_PASS)
    return mail


def fetch_emails(mail):
    """Fetch emails from the inbox."""
    mail.select("inbox", readonly=True)  # Select the mailbox you want to check
    status, messages = mail.search(None, "ALL")  # Search for all emails
    email_ids = messages[0].split()
    email_metadata_list = []
    hashes = getAllEmailHashes()
    new = False

    for email_id in email_ids:
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                email_metadata = extract_email_metadata(msg)
                if email_metadata["hash"] in hashes:
                    continue
                mail.store(email_id, "-FLAGS", "\\Seen")
                new = True
                email_metadata_list.append(email_metadata)
                email_queue.put(email_metadata)
                if PRINT:
                    print_email_metadata(email_metadata)

    return email_metadata_list, new


def extract_email_metadata(msg):
    """Extract metadata from an email message."""
    metadata = {
        "datetime": extract_date(msg),
        "subject": extract_subject(msg),
        "sender": extract_sender(msg),
        "recipient": extract_recipient(msg),
        "body": extract_body(msg),
        "hash": sha256(msg.as_bytes()).hexdigest(),
        "size": len(msg.as_bytes()),
    }
    return metadata


def extract_date(msg):
    """Extract the date from an email message."""
    date_str = msg.get("Date", "")
    if date_str:
        date = email.utils.parsedate_to_datetime(date_str)
        return date.strftime("%Y-%m-%d %H:%M:%S")
    return "No Date Provided"


def extract_subject(msg):
    """Extract the subject from an email message."""
    subject, encoding = decode_header(msg.get("Subject", ""))[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding if encoding else "utf-8")
    return subject


def extract_sender(msg):
    """Extract the sender from an email message."""
    return msg.get("From", "No Sender Provided")


def extract_recipient(msg):
    """Extract the recipient(s) from an email message."""
    return msg.get("To", "No Recipient Provided")


def extract_body(msg):
    """Extract the body from an email message."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if "attachment" not in content_disposition:
                body = ""
                for piece in part.get_payload():
                    body += str(piece)
                return body
    else:
        return msg.get_payload(decode=True).decode()


def getAllEmailHashes():
    """Fetch all email hashes from the database."""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS email (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hash TEXT UNIQUE,
                size INTEGER,
                datetime TEXT,
                subject TEXT,
                recipient TEXT,
                sender TEXT,
                body TEXT
                ) """
        )
        c.execute("SELECT hash FROM email")
        hashes = {row[0] for row in c.fetchall()}
    return hashes


def process_emails():
    """Process emails from the queue and insert them into the database."""
    hashes = getAllEmailHashes()
    while True:
        email_metadata = email_queue.get()
        if email_metadata["hash"] in hashes:
            email_queue.task_done()
            continue

        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO email (hash, datetime, subject, recipient, sender, body, size) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    email_metadata["hash"],
                    email_metadata["datetime"],
                    email_metadata["subject"],
                    email_metadata["recipient"],
                    email_metadata["sender"],
                    email_metadata["body"],
                    email_metadata["size"],
                ),
            )
            print(email_metadata["hash"])
            hashes.add(email_metadata["hash"])
            print(email_metadata["subject"])
            conn.commit()
        email_queue.task_done()
    print("Done!")


def monitor_emails():
    """Monitor for new emails."""
    mail = connect_to_imap()
    threading.Thread(target=process_emails, daemon=True).start()
    with open(COUNT_FILE, "r") as f:
        count = int(f.readlines()[0])
    while True:
        with open(COUNT_FILE, "w") as f:
            f.write(str(count + 1))
        count += 1
        mail = connect_to_imap()
        print(f"Checking for new emails at {datetime.now()}", f"Count: {count}")
        value = fetch_emails(mail)[1]

    # Start the worker thread


def getMetadata():
    """Fetch emails and return metadata as a list of dictionaries."""
    mail = connect_to_imap()
    email_metadata_list, _ = fetch_emails(mail)
    return email_metadata_list


def print_email_metadata(metadata):
    """Print email metadata."""
    print(f'Date: {metadata["datetime"]}')
    print(f'Subject: {metadata["subject"]}')
    print(f'From: {metadata["sender"]}')
    print(f'To: {metadata["recipient"]}')
    print(f'Body: {metadata["body"]}')
    print(f'Hash: {metadata["hash"]}')
    print(f'Size: {metadata["size"]}')
    print("-" * 50)


if __name__ == "__main__":
    PRINT = False
    hashes = getAllEmailHashes()
    print("Hashes Got")
    PROCESS = True
    print("Starting Monitor")
    monitor_emails()
    print(email_queue.qsize())
    print("Monitored")
    process_emails()
    print("Proessed Emails!")
