import pandas as pd
from pathlib import Path
import json


class InvalidDaylioTable(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class ColumnInfo:

    def __init__(self, name: str, type_name: str, kind: str):
        self.name = name
        self.type_name = type_name
        self.kind = kind

class DaylioCleaner:
    
    def __init__(self, name: str, df: pd.DataFrame, columns: list[ColumnInfo]):
        self.name = name
        self.table = df
        self.column_info = columns
        
        self.__fix_dates()
        
        if self.name == 'customMoods':
            self.table['mood_value'] = 6 - self.table['mood_group_id']
            for _, mood in self.table[(self.table['mood_group_id'].isin([2, 3, 4])) &
                       (self.table['mood_group_order'] == 0)].iterrows():
                match mood['mood_group_id']:
                    case 2:
                        mood['custom_name'] = 'Good'
                    case 3:
                        mood['custom_name'] = 'Meh'
                    case 4:
                        mood['custom_name'] = 'Bad'
    
    
    def __fix_dates(self):
        field_to_create = "none"
        for col in [x for x in self.column_info if x.type_name == 'timestamp']:
            match col.name:
                case 'createdAt' | "datetime" | "created_at":
                    field_to_create = "date"
                case 'end_date':
                    field_to_create = 'date_end'
                case _:
                    field_to_create = 'none'
            if field_to_create == 'none':
                continue
            else:
                self.table[col.name] = self.table[col.name].replace(0, pd.NaT)
                if self.name == 'goals':
                    self.table[col.name] = self.table[col.name].replace(-1, pd.NaT)
                self.table[col.name] = pd.to_datetime(self.table[col.name], unit='ms')
                self.table[field_to_create] = pd.to_datetime(self.table[col.name].dt.date)

    def to_sql(self, connection):
        cols = [x.name for x in self.column_info]
        self.table[cols].to_sql(self.name, connection, if_exists='replace', index=False)


def create_entry_tags(entries: DaylioCleaner, columns: list[ColumnInfo]):
    if entries.name != 'dayEntries':
        raise InvalidDaylioTable('Must past "dayEntries" table to create entry tags')
    tags_df = entries.table[['id', 'tags']].explode('tags')
    tags_df = tags_df.rename(columns={'id': 'entry_id', 'tags': 'tag'})
    with pd.option_context('future.no_silent_downcasting', True):
        tags_df['tag'] = tags_df['tag'].fillna(0).astype(int)

    return DaylioCleaner('entry_tags', tags_df, columns)


def create_mood_groups(columns: list[ColumnInfo]) -> DaylioCleaner:
    mood_groups_path = Path.cwd() / "data" / "mood_groups.json"
    df = pd.read_json(mood_groups_path)
    return DaylioCleaner('mood_groups', df, columns)


def get_table_info(table_name: str) -> list[ColumnInfo]:
    table_info_path = Path.cwd() / 'data' / 'table_info.json'
    json_data = json.loads(table_info_path.read_text())
    return [ColumnInfo(**data) for data in json_data[table_name]]