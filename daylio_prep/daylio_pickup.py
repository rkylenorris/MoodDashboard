from pathlib import Path
from datetime import datetime
import os
import base64
import json
import zipfile as zf
import shutil

class DaylipPickup:
    
    expected_cwd: str = "MoodDashboard"
    
    def __init__(self, pickup_dir: str = Path.home() / "OneDrive/DaylioData"):
        self.__set_cwd()
        
        self.pickup_dir = pickup_dir
        self.pickup_path = self.__find_backup_file()
        
        self.data_dir = Path.cwd() / "data"
        self.json_path = self.data_dir / "daylio.json"
        
        selected_tables_path = self.data_dir / "tables_needed.txt"
        self.selected_tables = [table.strip() for table in selected_tables_path.read_text().split('\n')]
    
    def __set_cwd(self):
        if Path.cwd().name != self.expected_cwd:
            for folder in Path.home().rglob(self.expected_cwd):
                if folder.is_dir() and folder.name == self.expected_cwd:
                    os.chdir(str(folder))
                    break
            else:
                raise FileNotFoundError(f'{self.expected_cwd} does not exist')
    
    def __find_backup_file(self):
        pickup_path = Path(self.pickup_dir, datetime.today().strftime('backup_%Y_%m_%d.daylio'))
        if pickup_path.exists():
            return pickup_path
        else:
            raise FileNotFoundError(f"{pickup_path} does not exist")
    
    def extract_backup(self):
        with zf.ZipFile(self.pickup_path, 'r') as zr:
            zr.extractall(self.data_dir)
            shutil.rmtree((self.data_dir / "assets"))
            
    
    def decode_backup_to_json(self):
        backup_path = self.data_dir / "backup.daylio"
        
        with open(str(backup_path), 'r') as backup:
            contents = base64.b64decode(backup.read()).decode("utf-8")
            
        data = json.loads(contents)
        
        return data
    
    def save_to_json(self, daylio_data):
        selected_tables_data = {table: daylio_data[table] for table in self.selected_tables}
        if self.json_path.exists():
            os.remove(self.json_path)
        
        with open(str(self.json_path), "W", encoding='utf-8') as j:
            json.dump(selected_tables_data, j, indent=4)
    
    def archive_json(self):
        date_str = datetime.today().strftime('%Y%m%d_%H%M')
        archive_path = self.data_dir / "archive" / f"daylio_{date_str}.json"
        shutil.copy(self.json_path, archive_path)