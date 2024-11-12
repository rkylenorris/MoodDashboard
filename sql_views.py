import sqlite3
from pathlib import Path


def view_exists(name: str = '%') -> bool:
    conn = sqlite3.connect(r'C:\Users\roder\Code\Python\DaylioDash\data\daylio.db')
    cursor = conn.cursor()
    cursor.execute(r"SELECT COUNT(1) as [exists] FROM sqlite_master "
                   r"WHERE type = 'view' and name like ?", (name,))
    exists = cursor.fetchone()[0]
    conn.close()
    if exists > 0:
        return True
    else:
        return False


if __name__ == '__main__':
    print(view_exists('v_daily_avgs'))
