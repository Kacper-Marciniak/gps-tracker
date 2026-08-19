from collections import deque
from app.integration.names import SERVER_LOG_NAME, LOG_NAME

def get_logs(filename: str, max_lines: int = 1000):
    try:
        with open(filename, "r", encoding="utf-8", errors="replace") as f:
            return list(reversed(deque(f, maxlen=max_lines)))
        
    except FileNotFoundError:
        return [f"Log file not found: {filename}"]

    except OSError as e:
        return [f"Error reading log file: {e}"]

def get_server_logs(max_lines: int = 1000):
    return get_logs(SERVER_LOG_NAME, max_lines)

def get_app_logs(max_lines: int = 1000):
    return get_logs(LOG_NAME, max_lines)