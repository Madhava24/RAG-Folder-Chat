import sqlite3
import pandas as pd
import config

def get_db_connection(db_path: str):
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable named column access
    return conn

def excecute_query(conn, query: str):
    """Executes a SQL query and returns the results."""
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    return [dict(row) for row in results]

def create_tables_from_df(dfs: list[tuple[str, pd.DataFrame]]):
    """Creates tables in the database from a list of DataFrames."""
    conn = get_db_connection(config.DB_PATH)
    count=0
    for table_name, df in dfs:
        try:
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            conn.commit()
            count+=1
        except Exception as e:
            print(f"Error creating table {table_name}: {e}")
    conn.close()
    return count

def get_table_ddl(conn, table_name: str) -> str:
    """Retrieves the DDL statement for a given table."""
    cursor = conn.cursor()
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    result = cursor.fetchone()
    return result['sql'] if result else ''