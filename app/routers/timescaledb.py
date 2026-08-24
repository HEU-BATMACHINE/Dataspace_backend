import os
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import UploadFile, File
import os
from fastapi.responses import PlainTextResponse
import psycopg2
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import pandas.io.sql as sqlio
from io import StringIO

router = APIRouter(tags=["timescaleDB"], prefix="/timescaledb")

# postgreSQL - timescaleDB
if "POSTGRESQL_HOST" in os.environ:
    POSTGRESQL_USER = os.environ.get("POSTGRESQL_USER")
    POSTGRESQL_PASSWORD = os.environ.get("POSTGRESQL_PASSWORD")
    POSTGRESQL_HOST = os.environ.get("POSTGRESQL_HOST")
    try:
        POSTGRESQL_PORT = int(os.environ.get("POSTGRESQL_PORT"))
    except:
        POSTGRESQL_PORT = 5432


def get_connection(dbname: str):
    """
    Establishes a connection to a PostgreSQL database.

    Parameters:
    - dbname (str): The name of the database to connect to.

    Returns:
    - psycopg2.extensions.connection: A connection object to the PostgreSQL database.

    Raises:
    - psycopg2.OperationalError: If an error occurs while connecting to the database.
    """
    try:
        # Establish a connection to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=dbname,
            user=POSTGRESQL_USER,
            password=POSTGRESQL_PASSWORD,
            host=POSTGRESQL_HOST,
            port=POSTGRESQL_PORT,
        )
        return conn
    except psycopg2.OperationalError as e:
        # Handle connection errors
        raise psycopg2.OperationalError(f"Failed to connect to database: {e}")


@router.get("/databases")
def list_databases() -> list[str]:
    """
    List all databases in timescaleDB. 

    SELECT datname FROM pg_database WHERE datistemplate = false

    Parameters:
    - dbname(str): Database to query

    Returns:
    - databases(list[str]): All database names
    """
    # Connect to the default database ('postgres'), which is always present
    conn = get_connection("postgres")

    # Required to execute SELECT without needing to commit
    conn.autocommit = True

    # Execute the SQL query to get the list of databases
    with conn.cursor() as cur:
        cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        results = cur.fetchall()
        databases = [x[0] for x in results]

    return databases


@router.get("/{dbname}", summary="Get tableIds")
def get_tableids(dbname: str) -> list[str]:
    """
    Return all tableIds in a database.

    SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'

    Parameters:
    - dbname(str): Database to query

    Returns:
    - all_table_names(list[str]): All tableIds in database
    """
    #https://stackoverflow.com/questions/14730228/postgresql-query-to-list-all-table-names

    sql_query = "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'"
    response = query_database(dbname, sql_query)
    result = response["results"]
    all_table_names = [x[0] for x in result]
    return all_table_names


@router.post("/{dbname}")
def create_database(dbname : str):
    """
    Create a database.

    CREATE DATABASE {dbname}

    Parameters:
    - dbname(str): Database to create

    Returns:
    - dict: Response
    """

    conn = get_connection("postgres")

    # Auto-commit must be enabled to run these queries
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    with conn.cursor() as cur:
        cur.execute(f"CREATE DATABASE {dbname}") 

    return {"detail": f"Created database {dbname}"}


@router.delete("/{dbname}")
def delete_database(dbname : str):
    """
    Delete a database. Does not allow deletion of postgreSQL required databases.

    DROP DATABASE {dbname}

    Parameters:
    - dbname(str): Database to delete

    Returns:
    - dict: Response
    """
    if dbname in ["postgres", "template0", "template1"]:
        return {"error":"Database cannot be removed",
                "detail": f"Database {dbname} in ['postgres', 'template0', 'template1']"}

    conn = get_connection("postgres")

    # Auto-commit must be enabled to run these queries
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    with conn.cursor() as cur:
        cur.execute(f"DROP DATABASE {dbname}") 

    return {"detail": f"Deleted database {dbname}"}


@router.post("/{dbname}/query")
def query_database(dbname : str, sql_query : str) -> dict:
    """
    Executes SQL query.

    Parameters:
    - dbname (str): The name of the database to query.
    - sql_query(str): The SQL query.

    Returns:
    - dict: Contains results from "fetchall" and SQL query that was used.
    """

    conn = get_connection(dbname)
    try:
        with conn.cursor() as cur:
            cur.execute(sql_query) 
            try:
                results = cur.fetchall()
            except Exception as e:
                print("Ignoring error: " + str(e))
                results = []
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"results": results, "sql_query": sql_query}


@router.post("/{dbname}/init")
def initialize_database(dbname : str):
    """
    Initialize SQL database. This is done in 3 steps.

    1. Delete database if it exists
    2. Create a new database
    3. Execute initialization query 

    Parameters:
    - dbname (str): The name of the database to initialize.

    Returns:
    - dict: Response from query_database.
    """

    try:
        delete_database(dbname)
    except psycopg2.errors.InvalidCatalogName:
        print(f"Database {dbname} does not exist, ignore deletion")

    create_database(dbname)

    # Get the path to the SQL file from the filepath of this script
    root_folder = Path(__file__).resolve().parent.parent.parent
    init_file = root_folder / 'timescaledb'/ 'init.sql' 

    # Read and execute query
    with open(init_file, 'r') as file:
        sql_query = file.read()
    response = query_database(dbname, sql_query)
    return response


@router.post("/{dbname}/timestamp")
def query_timestamp(dbname: str, tableids: list[str], timestamp1 : datetime, timestamp2 : datetime):
    """
    Query for all data between two times.

    Verifies that the tableId is in timescaleDB database.

    SELECT * FROM {tableid} WHERE time BETWEEN '{timestamp1}' AND '{timestamp2}'

    Parameters:
    - dbname(str): Database to connect to.
    - tableIds(list[str]): Tables to query.
    - timestamp1(datetime): Starting time.
    - timestamp2(datetime): End time.

    Returns:
    - results(dict): Dictionary containing the tableId as key and filtered (time,value) pairs as value.
    """

    # Check that tableId is in timescaleDB database
    all_tableIds = get_tableids(dbname)
    for tableId in tableids:
        if tableId.lower() not in all_tableIds:
            raise HTTPException(status_code=400, detail=f"TableId {tableId} not in database {dbname}.")

    # Query for data, store them in a dictionary where key is the tableId
    results = {}
    for tableId in tableids:
        sql_query = f"SELECT * FROM {tableId} WHERE time BETWEEN '{timestamp1}' AND '{timestamp2}' "
        results[tableId] = query_database(dbname, sql_query)["results"]

    return results


@router.get("/{dbname}/{tableId}.csv", response_class = PlainTextResponse)
def get_tableid_csv(dbname: str, tableId: str,limit:int=50):
    """
    Get all data from table in database, sorted by time, in CSV.

    SELECT * FROM {tableId} ORDER BY time DESC

    Parameters:
    - dbname(str): Database to connect to.
    - tableId(str): Table to query.

    Returns:
    - output_csv(str): Table as a CSV file in string format
    """
    sql_query = f"SELECT * FROM {tableId} ORDER BY time DESC LIMIT {limit}" 


    # Save response as Pandas dataframe
    conn = get_connection(dbname)
    df = sqlio.read_sql_query(sql_query, conn)

    # Save response to csv, then to str
    outputIO = StringIO()
    df.to_csv(outputIO, index=False)
    output_csv = outputIO.getvalue()

    return output_csv


@router.get("/{dbname}/{tableId}")
def get_tableid(dbname: str, tableId: str):
    """
    Get all data from table in database, sorted by time.

    SELECT * FROM {tableId} ORDER BY time DESC

    Parameters:
    - dbname(str): Database to connect to.
    - tableId(str): Table to query.

    Returns:
    - response(dict): Results from SQL query.
    """
    sql_query = f"SELECT * FROM {tableId} ORDER BY time DESC"
    response = query_database(dbname, sql_query)
    return response


@router.post("/{dbname}/{tableId}")
def insert_tableid(dbname : str, tableId: str, value: float, timestamp : datetime | None = None):
    """
    Insert data into table using a SQL query.

    INSERT INTO {tableId} (time, {tableId}) VALUES ('{timestamp}',{value})

    Parameters:
    - dbname(str): Database to insert into.
    - tableId(str): Table to insert into.
    - value(float): Measured value.
    - timestamp(datetime, optional): When the value was measured. Defaults to "now".

    Returns:
    - response(dict): Response from SQL insertion.
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)
    sql_query = f"INSERT INTO {tableId} (time, {tableId}) VALUES ('{timestamp}',{value})"
    response = query_database(dbname, sql_query)
    return response


@router.post("/{dbname}/{tableId}/upload_csv")
def upload_csv(dbname: str, tableId: str, file: UploadFile = File(...)):
    """
    Upload a CSV file and insert its contents into the specified table.
    The CSV should have two columns: timestamp (datetime) and value (float).

    Parameters:
    - dbname (str): Database to insert into.
    - tableId (str): Table to insert into.
    - file (UploadFile): CSV file to upload.

    Returns:
    - response (dict): Status message.
    """
    try:
        df = pd.read_csv(file.file)

        # Ensure correct column count
        if df.shape[1] != 2:
            raise HTTPException(status_code=400, detail="CSV must have exactly two columns: timestamp and value")

        # Rename columns
        df.columns = ["timestamp", "value"]

        # Prepare SQL insert statements
        values = ", ".join(f"('{row.timestamp}', {row.value})" for row in df.itertuples(index=False))
        sql_query = f"INSERT INTO {tableId} (time, {tableId}) VALUES {values}"

        query_database(dbname, sql_query)

        return {"message": "CSV data inserted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")
