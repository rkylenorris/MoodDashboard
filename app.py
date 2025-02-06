from daylio_prep import DaylipPickup, DaylioCleaner, ColumnInfo, create_entry_tags, create_mood_groups, get_table_info
from sql_cmds import create_tables, create_db_conn, insert_prefs, create_views, read_sql_view_to_df
from pathlib import Path
import pandas as pd
import logging
import logging.config
import json
import plotly.express as px
from datetime import datetime
from dash import dcc, html, dash
from dash.dependencies import Input, Output

start_time = datetime.now()

with open('log_config.json', 'r') as l:
    log_config = json.load(l)

logging.config.dictConfig(log_config)

logger = logging.getLogger(__name__)

logger.info("Process start...")

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
        daylio_tables.append(daylio_table)
        
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

# load sql db with daylio data
db_conn = create_db_conn()

for table in daylio_tables:
    table.to_sql(db_conn)

db_conn.commit()

insert_prefs(daylio_data['prefs'], db_conn)

# create views for easy grabbing of stats
create_views()

logger.info(f"Process ended, runtime: {(datetime.now() - start_time).total_seconds()}s")

# creating graphs

daily_avgs = read_sql_view_to_df(create_db_conn(), "v_daily_avgs")
fig = px.line(daily_avgs, x='day', y='avg_mood_value', title="Daily Average Mood Over 90 Days")

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Mood Dashboard"),
    dcc.Graph(id='mood-trend', figure=fig)
])

if __name__ == '__main__':
    app.run_server(debug=True)