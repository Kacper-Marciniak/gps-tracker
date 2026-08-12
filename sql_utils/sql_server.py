import sqlite3
import logging

logger = logging.getLogger(__name__)

TABLES = {
    "devices": {
        "id": "TEXT PRIMARY KEY",
        "ip": "TEXT NOT NULL",
        "gps_status": "BOOLEAN NOT NULL",
        "last_update": "DATETIME NOT NULL",
    },
    "gps_traces": {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "device_id": "INTEGER NOT NULL",
        "latitude": "REAL NOT NULL",
        "longitude": "REAL NOT NULL",
        "datetime": "DATETIME NOT NULL",
        "FOREIGN KEY(device_id)": "REFERENCES devices(id)",
    }
}

def init_database(database_name: str):
    with sqlite3.connect(database_name) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        # Create tables if they doesn't exist
        for table_name in TABLES.keys():
            query = f"CREATE TABLE IF NOT EXISTS {table_name}" + "(" + ", ".join([f"{col} {dtype}" for col, dtype in TABLES[table_name].items()]) + ")"
            logger.debug(f"Creating table {table_name} with query: {query}")
            cursor.execute(query)
            conn.commit()

# DEVICE

def insert_device(database_name: str, id: str, ip: str, gps_status: bool, last_datetime: str):
    if check_device_exists(database_name, id):
        logger.debug(f"Device with id {id} already exists. Updating instead of inserting.")
        return update_device(database_name, id, ip, gps_status, last_datetime)
    
    with sqlite3.connect(database_name) as conn:
        cursor = conn.cursor()
        query = "INSERT INTO devices (id, ip, gps_status, last_update) VALUES (?, ?, ?, ?)"
        logger.debug(f"Inserting device with query: {query} and values: {id}, {ip}, {gps_status}, {last_datetime}")
        cursor.execute(query, (id, ip, gps_status, last_datetime))
        conn.commit()
        return cursor.lastrowid

def update_device(database_name: str, id: str, ip: str, gps_status: bool, last_datetime: str):
    with sqlite3.connect(database_name) as conn:
        cursor = conn.cursor()
        query = "UPDATE devices SET ip = ?, gps_status = ?, last_update = ? WHERE id = ?"
        logger.debug(f"Updating device with query: {query} and values: {ip}, {gps_status}, {last_datetime}, {id}")
        cursor.execute(query, (ip, gps_status, last_datetime, id))
        conn.commit()
        return cursor.rowcount

def check_device_exists(database_name: str, id: str) -> bool:
    with sqlite3.connect(database_name) as conn:
        cursor = conn.cursor()
        query = "SELECT 1 FROM devices WHERE id = ?"
        logger.debug(f"Checking if device exists with query: {query} and id: {id}")
        cursor.execute(query, (id,))
        return cursor.fetchone() is not None

# GPS TRACE

def insert_gps_trace(database_name: str, device_id: str, latitude: float, longitude: float, datetime_str: str):
    with sqlite3.connect(database_name) as conn:
        cursor = conn.cursor()
        query = "INSERT INTO gps_traces (device_id, latitude, longitude, datetime) VALUES (?, ?, ?, ?)"
        logger.debug(f"Inserting GPS trace with query: {query} and values: {device_id}, {latitude}, {longitude}, {datetime_str}")
        cursor.execute(query, (device_id, latitude, longitude, datetime_str))
        conn.commit()
        return cursor.lastrowid

def get_last_gps_trace(database_name: str, device_id: int):
    with sqlite3.connect(database_name) as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM gps_traces WHERE device_id = ? ORDER BY datetime DESC LIMIT 1"
        logger.debug(f"Fetching last GPS trace with query: {query} and device_id: {device_id}")
        cursor.execute(query, (device_id,))
        return cursor.fetchone()

# UTILS

def export_table_json(database_name: str, table_name: str):
    with sqlite3.connect(database_name) as conn:
        cursor = conn.cursor()
        query = f"SELECT * FROM {table_name}"
        logger.debug(f"Exporting data to JSON with query: {query}")
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]
        return result

def export_database(database_name: str, export_path: str):
    import json
    data = {}
    for table_name in TABLES.keys():
        data[table_name] = export_table_json(database_name, table_name)
    with open(export_path, 'w') as f:
        json.dump(data, f, indent=4)
    logger.info(f"Database exported to {export_path}")