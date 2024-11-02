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
        q_template = Template("DROP TABLE IF EXITS {{table_name}}")
        query = q_template.substitute(table_name=table)
        cursor.execute(query)

    create_tables_path = Path.cwd() / 'sql' / 'create_tables.sql'

    cursor.execute(create_tables_path.read_text())

    conn.commit()
    conn.close()


def insert_mood_groups():
    conn = sqlite3.connect('data/daylio.db')
    cursor = conn.cursor()
    mood_grps = [
        {
            "id": 1,
            'name': 'The Best Days',
            'value': 5
        },
        {
            "id": 2,
            'name': 'The Good Days',
            'value': 4
        },
        {
            "id": 3,
            'name': 'The Meh Days',
            'value': 3
        },
        {
            "id": 4,
            'name': 'The Bad Days',
            'value': 2
        },
        {
            "id": 5,
            'name': 'The Worst Days',
            'value': 1
        },
    ]
    select_query = '''
    INSERT INTO mood_groups (id, name, value)
    VALUES (?, ?, ?)
    '''
    for grp in mood_grps:
        cursor.execute(select_query, (grp['id'], grp['name'], grp['value']))

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
