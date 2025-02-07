from daylio_prep import DaylipPickup, DaylioCleaner, ColumnInfo, create_entry_tags, create_mood_groups, get_table_info
from sql_cmds import create_tables, create_db_conn, insert_prefs, create_views, read_sql_view_to_df
from pathlib import Path
import pandas as pd
import logging
import logging.config
import json
import plotly.express as px
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
from dash import dcc, html, dash
from dash.dependencies import Input, Output
from plotly.graph_objects import Figure
import plotly.io as pio

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
daily_avgs['day'] = pd.to_datetime(daily_avgs['day'])
activity_summary = read_sql_view_to_df(create_db_conn(), "v_activity_summary")


colors = px.colors.qualitative.Dark2
fig = px.scatter(daily_avgs, x='day', y='avg_mood_value',
                 template='plotly_dark',
                 color_discrete_sequence=colors,
                 trendline='ols',
                 title="Avg Mood Per Day (Past 90 Days)")

fig.update_layout(yaxis_range=[1, 5])
fig.update_traces(mode='lines')
fig.data[-1].line.color = 'red'

fig_activity = px.bar(activity_summary, x='activity', y='count', color='group', title='Activity Summary Over 90 Days', template='plotly_dark')

today = datetime.today()
ninety_days_ago = today - timedelta(days=90)
today_str = today.strftime('%Y-%m-%d')
ninety_str = ninety_days_ago.strftime('%Y-%m-%d')
date_range = f"Date Range: {ninety_str} - {today_str}"

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

image_path = app.get_asset_url('logo.png')

app.layout = dbc.Container([
    dbc.Container([
        # html.H1('Mood Dash'),
        html.Img(src=image_path, height=275),
        html.H4(date_range, style={'color': 'grey'})
        ], style={'textAlign': 'center'}),
    dbc.Container([
        dcc.Graph(id='mood-trend', figure=fig),
        dcc.Graph(id='activity-summary', figure=fig_activity)
    ])
], style={'backgroundColor': 'black'})

if __name__ == '__main__':
    app.run_server(debug=True)