import sqlite3
from datetime import datetime


def create_db_conn() -> sqlite3.Connection:
    """
    creates a new database connection to the SQLite database
    :return:
    """
    return sqlite3.connect('data/daylio.db')


def get_last_entry_date(conn=create_db_conn()):
    cur = conn.cursor()
    cur.execute(f"SELECT [LAST_ENTRY_CREATION_TIME] FROM prefs")
    date_string = cur.fetchone()[0]
    return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S.%f').date()
