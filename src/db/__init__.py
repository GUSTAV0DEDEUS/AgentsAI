import sqlite3
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
DB_NAME = "db.sqlite3"
DATABASE_FILE = ROOT_DIR / DB_NAME  

connection = sqlite3.connect(DATABASE_FILE, check_same_thread=False)
cursor = connection.cursor()
TABLE_NAME = "customers"    


### Create the database and table if they do not exist
cursor.execute(
    f'CREATE TABLE IF NOT EXISTS {TABLE_NAME}'
    '('
    'id INTEGER PRIMARY KEY AUTOINCREMENT,'
    'name TEXT,'
    'weight REAL'
    ')'
)
connection.commit()

### Insert sample data
cursor.execute(
    f'INSERT INTO {TABLE_NAME} (name, weight) VALUES (?, ?)',
    ('John Doe', 70.5)
)

cursor.execute(
    f'INSERT INTO {TABLE_NAME} (name, weight) VALUES (?, ?)',
    ('Jane Smith', 65.0)
)

connection.commit()
cursor.close()
connection.close()