import sqlite3
from datetime import datetime
from string import Template
from pathlib import Path
# Connect to SQLite database (or create it)


def create_daylio_sql_tables():
    """
    function to drop all tables from db, then recreate accordingly

    :return:
    """
    conn = sqlite3.connect('data/daylio.db')
    cursor = conn.cursor()
    tables = [
        'customMoods',
        'tags',
        'dayEntries',
        'goals',
        'prefs',
        'tag_groups',
        'goalEntries',
        'calendar',
        'mood_groups',
        'entry_tags',
    ]

    for table in tables:
        q_template = Template("DROP TABLE IF EXISTS $table_name")
        query = q_template.substitute(table_name=table)
        cursor.execute(query)

    create_tables_path = Path.cwd() / 'sql' / 'create_tables.sql'

    cursor.executescript(create_tables_path.read_text())

    conn.commit()
    conn.close()


def insert_prefs(prefs_dict):
    conn = sqlite3.connect('data/daylio.db')
    cursor = conn.cursor()
    insert_query = '''
    INSERT INTO prefs 
    (AUTO_BACKUP_IS_ON, LAST_DAYS_IN_ROWS_NUMBER, DAYS_IN_ROW_LONGEST_CHAIN, LAST_ENTRY_CREATION_TIME) 
    VALUES (?, ?, ?, ?)
    '''
    bckup = next(filter(lambda x: x['key'] == 'AUTO_BACKUP_IS_ON', prefs_dict))['value']
    last_days_inarow = next(filter(lambda x: x['key'] == 'LAST_DAYS_IN_ROWS_NUMBER', prefs_dict))['value']
    longest_days_inarow = next(filter(lambda x: x['key'] == 'DAYS_IN_ROW_LONGEST_CHAIN', prefs_dict))['value']
    last_entry_time = next(filter(lambda x: x['key'] == 'LAST_ENTRY_CREATION_TIME', prefs_dict))['value']
    last_entry_time = datetime.fromtimestamp(last_entry_time/1000)
    vals = [bckup, last_days_inarow, longest_days_inarow, last_entry_time]
    cursor.execute(insert_query, vals)
    conn.commit()
    conn.close()
