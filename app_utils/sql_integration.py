from sql_utils import sql_server as sql
from datetime import datetime, timezone, timedelta


def get_devices_from_database(database_name: str):
    """
    Fetch all devices from the database.
    """
    devices = []
    for device in sql.get_all_devices(database_name):
        traces = get_gps_traces_last_N_hours(database_name, device_id=device[0], hours=24)

        devices.append({
            "id": device[0],
            "ip": device[1],
            "gps_status": bool(device[2]),
            "datetime": device[3],
            "latitude": traces[0]["latitude"] if traces else None,
            "longitude": traces[0]["longitude"] if traces else None,
            "traces": traces,
        })

    return devices

def get_gps_traces_last_N_hours(database_name: str, device_id: int, hours: float = 24):
    """
    Fetch GPS traces for a specific device (last N hours).
    """
    start_datetime = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
    traces = []
    for trace in sql.get_gps_traces_between_datetimes(database_name, device_id, start_datetime, end_datetime=None):
        traces.append({
            "latitude": trace[2],
            "longitude": trace[3],
            "datetime": trace[4],
        })
    print(traces)

    return traces