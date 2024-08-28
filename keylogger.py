import sqlite3
from datetime import datetime
from pynput import keyboard, mouse
import psutil
import time
import threading
from email1 import monitor_emails

# Database file
DB_FILE = "keylog.db"

# Create tables to store data if they don't exist


def create_tables():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS keylog (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        key TEXT,
                        timestamp TEXT,
                        application TEXT,
                        window_title TEXT,
                        key_hold_duration REAL
                    )"""
        )

        c.execute(
            """CREATE TABLE IF NOT EXISTS mouse_clicks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        button TEXT,
                        timestamp TEXT,
                        x INTEGER,
                        y INTEGER
                    )"""
        )

        c.execute(
            """CREATE TABLE IF NOT EXISTS mouse_paths (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        x INTEGER,
                        y INTEGER
                    )"""
        )

        c.execute(
            """CREATE TABLE IF NOT EXISTS idle_time (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        duration REAL
                    )"""
        )

        c.execute(
            """CREATE TABLE IF NOT EXISTS scroll_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        direction TEXT,
                        timestamp TEXT
                    )"""
        )

        conn.commit()


# Dictionary to keep track of key press times
key_press_times = {}


def get_active_window():
    active_window = None
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        if proc.info["pid"] == psutil.Process().pid:
            active_window = proc.info["name"]
    return active_window


def on_press(key):
    try:
        k = key.char
    except AttributeError:
        k = str(key)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    application = get_active_window()
    window_title = "N/A"  # Placeholder, as capturing the window title can be complex

    key_press_times[k] = time.time()

    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO keylog (key, timestamp, application, window_title, key_hold_duration) VALUES (?, ?, ?, ?, ?)",
            (k, timestamp, application, window_title, None),
        )
        conn.commit()


def on_release(key):
    try:
        k = key.char
    except AttributeError:
        k = str(key)

    if k in key_press_times:
        key_hold_duration = time.time() - key_press_times[k]
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute(
                "UPDATE keylog SET key_hold_duration = ? WHERE key = ? AND key_hold_duration IS NULL",
                (key_hold_duration, k),
            )
            conn.commit()
        del key_press_times[k]


def on_click(x, y, button, pressed):
    if pressed:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO mouse_clicks (button, timestamp, x, y) VALUES (?, ?, ?, ?)",
                (button.name, timestamp, x, y),
            )
            conn.commit()


def on_move(x, y):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO mouse_paths (timestamp, x, y) VALUES (?, ?, ?)",
            (timestamp, x, y),
        )
        conn.commit()


def on_scroll(x, y, dx, dy):
    direction = "up" if dy > 0 else "down"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO scroll_events (direction, timestamp) VALUES (?, ?)",
            (direction, timestamp),
        )
        conn.commit()


def record_idle_time():
    last_active = time.time()
    try:
        while True:
            idle_time = psutil.cpu_times().idle
            if (
                idle_time > 60
            ):  # Consider as idle if idle time is greater than 60 seconds
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                duration = time.time() - last_active
                with sqlite3.connect(DB_FILE) as conn:
                    c = conn.cursor()
                    c.execute(
                        "INSERT INTO idle_time (timestamp, duration) VALUES (?, ?)",
                        (timestamp, duration),
                    )
                    conn.commit()
                last_active = time.time()
            time.sleep(60)
    except KeyboardInterrupt:
        print("Stopping")


# Create tables if they don't exist
create_tables()
# start emails in a new thread
# emails_thread = threading.Thread(target=emails)
# emails_thread.daemon = True
# emails_thread.start()
# print("Emails Complete")
# Start the idle time recording in a separate thread
print("Idle")
idle_thread = threading.Thread(target=record_idle_time)
idle_thread.daemon = True
idle_thread.start()
# print("Emails")
# emails_thread = threading.Thread(target=monitor_emails)
# emails_thread.daemon = True
# emails_thread.start()


# Start the key and mouse listeners
with keyboard.Listener(
    on_press=on_press, on_release=on_release
) as key_listener, mouse.Listener(
    on_click=on_click, on_move=on_move, on_scroll=on_scroll
) as mouse_listener:
    print("Keys")
    key_listener.join()
    print("Mouse")
    mouse_listener.join()
