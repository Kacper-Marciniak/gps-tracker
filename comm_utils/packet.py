# Protocol packet format
from enum import Enum
from datetime import datetime

class ProtocolType(Enum):
    LOGIN = "2A4851"
    TELEMETRY = "24"

class Packet:
    def __init__(self, byte_data: bytes):
        self.byte_data = byte_data
        self.hex_data = byte_data.hex().upper()

        for key, value in ProtocolType.__members__.items():
            if self.hex_data.startswith(value.value):
                self.protocol_type = value
                break
        else:
            raise ValueError(f"Unknown protocol type!")

    def get_type(self):
        return self.protocol_type

    def get_raw_hex(self):
        return self.hex_data
            
    def decode(self):
        if self.protocol_type == ProtocolType.LOGIN:
            return self.decode_login(), self.protocol_type
        elif self.protocol_type == ProtocolType.TELEMETRY:
            return self.decode_telemetry(), self.protocol_type
        else:
            raise ValueError(f"Unknown protocol type! {self.protocol_type}")

    def decode_login(self):
        hex_str = self.hex_data.strip().replace(" ", "").lower()
        ascii_text = bytes.fromhex(hex_str).decode('ascii', errors='ignore').strip()

        if ascii_text.startswith('*') and ascii_text.endswith('#'):
            payload = ascii_text[1:-1] # between * a #
        else:
            payload = ascii_text
        payload = payload.split(',')
    
        if len(payload) < 15:
            raise ValueError(f"Incomplete HQ frame: expected at least 15 fields, got {len(payload)}")
        
        datetime_utc = datetime.strptime(payload[3] + payload[11], "%H%M%S%d%m%y")
        datetime_sql = datetime_utc.strftime("%Y-%m-%d %H:%M:%S")
        results = {
            'device_id': payload[1],                          
            'msg_type': payload[2],                                         # V1
            'datetime': datetime_sql,                                       # SQL DATETIME compatible string
            'gps_status': payload[4] == 'A',                                # A = valid, V = invalid
            'latitude_raw': f"{payload[5]} {payload[6]}",                   # 000000000 S
            'longitude_raw': f"{payload[7]} {payload[8]}",                  # 0000000000 W
            'speed_knots': float(payload[9]),                               # 0.00
            'heading_deg': int(payload[10]),                                # 0
            'status_hex': payload[12],                                      # fbfffbff
            'gsm': {
                'mcc': int(payload[13]),                                    # Country code (Poland = 260)
                'mnc': int(payload[14]),                                    # Network code
                'lac': int(payload[15]) if len(payload) > 15 else None,     # Location Area Code (LAC)
                'cell_id': int(payload[16]) if len(payload) > 16 else None  # Cell ID
            }
        }
    
        return results

    def decode_telemetry(self):
        hex_str = self.hex_data.strip().replace(" ", "").lower()

        if len(hex_str) < 24:
            raise ValueError(f"Incomplete telemetry frame: expected at least 24 hex characters, got {len(hex_str)}")

        def read_hex(start: int, end: int, default: str = "00") -> str:
            chunk = hex_str[start:end]
            return chunk if chunk else default

        def read_int(start: int, end: int, default: int = 0) -> int:
            chunk = hex_str[start:end]
            return int(chunk, 16) if chunk else default

        def read_direction(start: int, end: int, default: str) -> str:
            chunk = hex_str[start:end]
            if len(chunk) != 2:
                return default

            try:
                direction = chr(int(chunk, 16))
            except ValueError:
                return default

            return direction if direction in {"N", "S", "E", "W"} else default
        
        device_id = hex_str[2:12]
        
        datetime_utc = datetime.strptime(hex_str[12:24], "%H%M%S%d%m%y")
        datetime_sql = datetime_utc.strftime("%Y-%m-%d %H:%M:%S")
        
        raw_lat = hex_str[24:33]
        raw_lat_dir = read_direction(33, 35, 'N')
        raw_lon = hex_str[35:45]
        raw_lon_dir = read_direction(45, 47, 'E')
        
        if raw_lat.isdigit() and int(raw_lat) > 0:
            lat_deg = float(raw_lat[0:2]) + (float(raw_lat[2:]) / 10000.0) / 60.0
            lon_deg = float(raw_lon[0:3]) + (float(raw_lon[3:]) / 10000.0) / 60.0
            latitude = round(-lat_deg if raw_lat_dir == 'S' else lat_deg, 6)
            longitude = round(-lon_deg if raw_lon_dir == 'W' else lon_deg, 6)
        else:
            latitude = 0.0
            longitude = 0.0
        
        status_hex = read_hex(50, 58)
        status_int = int.from_bytes(bytes.fromhex(status_hex), byteorder='little')
        
        results = {
            'device_id': device_id,
            'latitude': latitude,
            'longitude': longitude,
            'datetime': datetime_sql,
            'speed_kmh': read_int(32, 34),
            'heading_deg': read_int(34, 38),
            'gps_status': bool(status_int),
            'status_flags': {
                'alarm_gas_cut': bool(status_int & (1 << 0)),
                'vehicle_fortified': bool(status_int & (1 << 1)),
                'low_battery_alarm': bool(status_int & (1 << 2)),
                'power_cut_alarm': bool(status_int & (1 << 3)),
                'shock_alarm': bool(status_int & (1 << 4)),
                'acc_ignition_on': bool(status_int & (1 << 5)), # Stan zapłonu
            },
            'gsm': {
                'lbs_count': read_int(74, 76),
                'mcc': read_int(76, 78),          # Mobile Country Code
                'mnc': read_int(78, 80),          # Mobile Network Code
                'lac': read_int(80, 84),          # Location Area Code
                'cell_id': read_int(84, 90),      # Cell ID
            }
        }
        
        return results

    def encode(self):
        self.byte_data = bytes.fromhex(self.hex_data)
        return self.byte_data

    @staticmethod
    def encode_login_response(device_id: int) -> bytes:
        text = f"*HQ,{device_id},AP00#\r\n"
        return text.encode('ascii')