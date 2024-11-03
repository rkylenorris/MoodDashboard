# imports
from pickup_data import DaylioDataPrep
from clean_data import DaylioTable, get_table_info, create_mood_groups, create_entry_tags
from create_calendar import write_calendar_to_db
from pathlib import Path
import json
import pandas as pd
import sqlite3


# section for picking up data
prep = DaylioDataPrep()
prep.extract_data()
prep.decode_backup()

# section for initializing db and creating tables
# TODO: add this section in

# section for loading extracted json data into class objects
data_dir = Path.cwd() / 'data'
daylio_data_path = data_dir / 'daylio.json'
daylio_data = json.loads(daylio_data_path.read_text())
tables = (data_dir / 'tables_needed.txt').read_text().split('\n')

daylio_tables = []

for table in tables:
    df = pd.DataFrame(daylio_data[table])
    column_info = get_table_info(table)
    daylio_table = DaylioTable(table, df, column_info)
    daylio_tables.append(daylio_table)
    if daylio_table.name == 'dayEntries':
        columns = get_table_info('entry_tags')
        daylio_tables.append(
            create_entry_tags(daylio_table, columns)
        )

mood_groups_columns = get_table_info('mood_groups')
daylio_tables.append(
    create_mood_groups(mood_groups_columns)
)

db_path = data_dir / 'daylio.db'

db_conn = sqlite3.connect(str(db_path))

for table in daylio_tables:
    table.to_sql(db_conn)

write_calendar_to_db(db_conn)

db_conn.commit()
db_conn.close()
