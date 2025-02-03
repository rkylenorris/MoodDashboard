import zipfile as zf
import os
import base64
from pathlib import Path
from datetime import datetime
import json
import shutil


class DaylioDataPrep:

    def __init__(self, pickup_dir: str = Path.home() / "OneDrive/DaylioData") -> None:
        self.pickup_dir = pickup_dir
        self.expected_cwd = 'MoodDashboard'
        self.backup_name = datetime.today().strftime('backup_%Y_%m_%d.daylio')
        self.__set_cwd()
        self.data_dir = Path.cwd() / "data"
        self.json_path = self.data_dir / "daylio.json"
        selected_tables_path = self.data_dir / 'tables_needed.txt'
        self.selected_tables = selected_tables_path.read_text().split('\n')

    def __set_cwd(self):
        if Path.cwd().name != self.expected_cwd:
            for folder in Path.home().rglob(self.expected_cwd):
                if folder.is_dir() and folder.name == self.expected_cwd:
                    os.chdir(str(folder))
                    break
            else:
                raise FileNotFoundError(f'{self.expected_cwd} does not exist')

    def __find_backup(self) -> Path:
        print('checking for today\'s backup file')
        backup_path = Path(self.pickup_dir , self.backup_name)
        if backup_path.exists():
            print(f'backup file found: {str(backup_path)}')
            return backup_path
        else:
            raise FileNotFoundError(f'{backup_path} does not exist')

    def extract_data(self) -> None:
        print("Extracting data..")
        with zf.ZipFile(self.__find_backup(), "r") as zip_ref:
            zip_ref.extractall(self.data_dir)
            shutil.rmtree(self.data_dir / 'assets')

    def decode_backup(self) -> None:
        backup_path = self.data_dir / 'backup.daylio'

        if not backup_path.exists():
            raise FileNotFoundError(f'{backup_path} does not exist')

        print('Decoding backup data..')
        with open(str(backup_path), "r") as backup:
            contents = base64.b64decode(backup.read()).decode("utf-8")

        data = json.loads(contents)

        select_data = {table: data[table] for table in self.selected_tables}

        print("Saving as json...")
        if self.json_path.exists():
            os.remove(self.json_path)

        with open(str(self.json_path), "w", encoding='utf-8') as j:
            json.dump(select_data, j, indent=4)

        self.__archive_backup()

    def __archive_backup(self) -> None:
        date_str = datetime.today().strftime('%Y%m%d_%H%M')
        archive_path = self.data_dir / "archive" / f"daylio_{date_str}.json"
        print(f'Creating archive file: {archive_path.name}')
        shutil.copy(self.json_path, archive_path)


if __name__ == '__main__':
    daylio = DaylioDataPrep()
    daylio.extract_data()
    daylio.decode_backup()
