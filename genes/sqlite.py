
from pathlib import Path
import sqlite3
from typing import List
import pandas as pd

def get_tables_from_database(database_path: Path) -> List[str]:
    # Connect to the SQLite database
    conn = sqlite3.connect(str(database_path))
    cursor = conn.cursor()

    # Execute the SQL query to get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")

    # Fetch all table names
    tables = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Extract table names from the fetched rows
    table_names = [table[0] for table in tables]

    return table_names

import sqlite3
from typing import List, Tuple

def select_rows(database_path: str, table_name: str, num_rows: int) -> List[Tuple]:
    # Connect to the SQLite database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Execute the SQL query to select the specified number of rows
    cursor.execute(f'SELECT * FROM {table_name} LIMIT ?', (num_rows,))

    # Fetch the selected rows
    rows = cursor.fetchall()

    # Close the database connection
    conn.close()

    return rows

def get_table_df(database_path: str, table_name: str = "variant") -> pd.DataFrame:
    conn = sqlite3.connect(database_path)
    sql_query = f'SELECT * FROM {table_name}'
    df = pd.read_sql_query(sql_query, conn)
    return df