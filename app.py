from daylio_prep import DaylipPickup, DaylioCleaner, ColumnInfo, create_entry_tags, create_mood_groups, get_table_info
from sql_cmds import create_tables, create_db_conn, insert_prefs
from pathlib import Path
import pandas as pd

# get backup, extract to data directory, decode to json, save, and archive json
pickup = DaylipPickup()

pickup.extract_backup()
daylio_data = pickup.decode_backup_to_json()
pickup.save_to_json(daylio_data=daylio_data)
pickup.archive_json()

# initialize db and create tables
create_tables()

# load daylio json data into class objects
data_dir = Path.cwd() / 'data'
tables = [table.strip() for table in (data_dir / 'tables_needed.txt').read_text().split('\n')]
daylio_tables = []

for table in tables:
    if table != "prefs":
        df = pd.DataFrame(daylio_data[table])
        column_info = get_table_info(table)
        daylio_table = DaylioCleaner(table, df, column_info)
        daylio_tables.append(
            daylio_table
        )
        
        if daylio_table.name == 'dayEntries':
            columns = get_table_info('entry_tags')
            daylio_tables.append(
                create_entry_tags(daylio_table, columns)
            )

daylio_tables.append(
    create_mood_groups(
        get_table_info('mood_groups')
    )
)

db_conn = create_db_conn()

for table in daylio_tables:
    table.to_sql(db_conn)

db_conn.commit()

insert_prefs(daylio_data['prefs'], db_conn)
