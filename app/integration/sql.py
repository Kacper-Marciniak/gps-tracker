from sql_utils import sql_server as sql
from datetime import datetime, timezone, timedelta
from app.integration.names import DATABASE_NAME

def get_devices_from_database():
    """
    Fetch all devices from the database.
    """
    devices = []
    for device in sql.get_all_devices(DATABASE_NAME):

        devices.append({
            "label": f"ID:{device[0]}",
            "value": device[0],
        })

    return devices

def get_device_traces(device_id: int, date_range: tuple = None):
    """
    Fetch traces for a specific device from the database within a given date range.
    """
    traces = []
    for trace in sql.get_gps_traces_between_datetimes(DATABASE_NAME, device_id, date_range[0], end_datetime=date_range[1]):
        traces.append({
            "latitude": trace[2],
            "longitude": trace[3],
            "datetime": trace[4],
            "speed": trace[5],
            "heading": trace[6],
            "battery": trace[7],
        })
        
    return traces

def get_device_location(device_id: int):
    """
    Fetch device location from the database.
    """
    location = sql.get_last_gps_trace(DATABASE_NAME, device_id)
    if location is None:
        return None
    elif len(location) == 0:
        return None
    else:
        location = {
            "device_id": location[1],
            "latitude": location[2],
            "longitude": location[3],
            "datetime": location[4],
            "speed": location[5],
            "heading": location[6],
            "battery": location[7],
        }
        
    return location