
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import pyodbc
import pandas as pd
from dotenv import load_dotenv
import os
import sys



# Load environment variables from .env file
load_dotenv()
 
 # Read database URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)


# ── Connection string builder ─────────────────────────────────────────────────
 
def _build_connection_string(auth_mode: str = "windows") -> str:
    """
    Build the ODBC connection string from environment variables.
 
    Parameters
    ----------
    auth_mode : str
        'windows'  – Uses Windows Authentication (Trusted_Connection=yes).
                     Recommended for local development on Windows machines.
        'sql'      – Uses SQL Server Authentication (username + password).
                     Required when connecting from Linux/Mac or remote servers.
 
    Returns
    -------
    str : ODBC connection string
    """
    driver   = os.getenv("DB_DRIVER",   "ODBC Driver 18 for SQL Server")
    server   = os.getenv("DB_SERVER",   "localhost")
    database = os.getenv("DB_DATABASE", "GworldsoftAcademyDB")
 
    if auth_mode == "windows":
        # Windows Authentication — no username/password needed.
        # SQL Server verifies identity via your Windows login.
        conn_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
    elif auth_mode == "sql":
        # SQL Server Authentication — requires DB_USERNAME and DB_PASSWORD in .env
        username = os.getenv("DB_USERNAME", "")
        password = os.getenv("DB_PASSWORD", "")
        if not username or not password:
            raise ValueError(
                "SQL auth mode requires DB_USERNAME and DB_PASSWORD in your .env file."
            )
        conn_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
        )
    else:
        raise ValueError(f"Unknown auth_mode: '{auth_mode}'. Use 'windows' or 'sql'.")
 
    return conn_str
 
 
# ── Core connection function ──────────────────────────────────────────────────
 
def get_db_connection(auth_mode: str = "windows") -> pyodbc.Connection:
    """
    Establish and return a pyodbc connection to GworldsoftAcademyDB.
 
    Usage
    -----
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM StudentPerformance")
        conn.close()
 
    Parameters
    ----------
    auth_mode : str
        Authentication mode — 'windows' (default) or 'sql'.
 
    Returns
    -------
    pyodbc.Connection : Active database connection object
    """
    conn_str = _build_connection_string(auth_mode)
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as e:
        print(f"\n[ERROR] Could not connect to SQL Server.")
        print(f"  Error code : {e.args[0]}")
        print(f"  Message    : {e.args[1]}")
        print("\n[TROUBLESHOOTING TIPS]")
        print("  1. Ensure SQL Server (Developer Edition) is running — check SSMS.")
        print("  2. Verify DB_SERVER in your .env matches your instance name.")
        print(f"     Common values: 'localhost', '.', 'localhost\\SQLEXPRESS'")
        print("  3. Ensure 'ODBC Driver 18 for SQL Server' is installed.")
        print("     Download: https://aka.ms/downloadmsodbcsql")
        print("  4. Ensure Windows Authentication is enabled on the SQL Server instance.")
        sys.exit(1)
 
 
# ── Convenience: load full table into DataFrame ───────────────────────────────
 
def load_table(table_name: str = "StudentPerformance",
               auth_mode: str = "windows") -> pd.DataFrame:
    """
    Load an entire SQL Server table into a pandas DataFrame.
 
    Parameters
    ----------
    table_name : str
        Name of the table or view to query. Default: 'StudentPerformance'.
    auth_mode  : str
        Authentication mode — 'windows' or 'sql'.
 
    Returns
    -------
    pd.DataFrame
    """
    conn = get_db_connection(auth_mode)
    query = f"SELECT * FROM {table_name} ORDER BY student_id;"
    df = pd.read_sql(query, conn)
    conn.close()
    return df
 
 
def load_ml_view(auth_mode: str = "windows") -> pd.DataFrame:
    """
    Load the ML-ready view (vw_MLReadyDataset) which includes encoded
    columns (income_encoded, gender_encoded) and the derived feature
    (study_efficiency_ratio).
 
    Returns
    -------
    pd.DataFrame
    """
    conn = get_db_connection(auth_mode)
    query = "SELECT * FROM vw_MLReadyDataset ORDER BY student_id;"
    df = pd.read_sql(query, conn)
    conn.close()
    return df
 
 
def load_custom_query(query: str,
                      auth_mode: str = "windows") -> pd.DataFrame:
    """
    Execute a custom SQL query and return results as a DataFrame.
 
    Parameters
    ----------
    query     : str   – Any valid T-SQL SELECT statement.
    auth_mode : str   – 'windows' or 'sql'.
 
    Returns
    -------
    pd.DataFrame
    """
    conn = get_db_connection(auth_mode)
    df = pd.read_sql(query, conn)
    conn.close()
    return df
 
 
# ── Connection test (run this file directly to verify setup) ─────────────────
 
if __name__ == "__main__":
    print("=" * 60)
    print("  GworldsoftAcademy — Connection Test")
    print("=" * 60)
 
    print("\n[1/4] Loading environment variables from .env ...")
    server   = os.getenv("DB_SERVER",   "NOT SET")
    database = os.getenv("DB_DATABASE", "NOT SET")
    driver   = os.getenv("DB_DRIVER",   "NOT SET")
    print(f"  DB_SERVER   : {server}")
    print(f"  DB_DATABASE : {database}")
    print(f"  DB_DRIVER   : {driver}")
 
    print("\n[2/4] Attempting database connection ...")
    conn = get_db_connection(auth_mode="windows")
    print("Connection established successfully!")
 
    print("\n[3/4] Loading StudentPerformance table ...")
    df = load_table("StudentPerformance")
    print(f"Data loaded. Shape: {df.shape}")
    print(f"Rows   : {df.shape[0]:,}  (expected ≥ 1,000)")
    print(f"Columns: {df.shape[1]}")
 
    print("\n[4/4] Quick data preview:")
    print(df.head(3).to_string(index=False))
 
    print("\n[COLUMN SUMMARY]")
    print(df.dtypes.to_string())
 
    print("\n[NULL CHECK]")
    nulls = df.isnull().sum()
    print(nulls[nulls > 0] if nulls.any() else " No null values found.")
 
    # Validate row count requirement
    if df.shape[0] >= 1000:
        print(f"\n CONNECTION TEST PASSED — {df.shape[0]:,} rows loaded (≥ 1,000 required).")
    else:
        print(f"\n WARNING — Only {df.shape[0]} rows found. Re-run Phase1_DatabaseSetup.sql.")
 
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

    print("=" * 60)