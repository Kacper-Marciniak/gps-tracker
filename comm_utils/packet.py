# Protocol packet format
from enum import Enum
from datetime import datetime

PROTOCOL_TYPES = {
    "V1": "LOCATION_DATA",
    "XT": "HEARTBEAT",
    "VI1": "LOCATION_REQUEST",
    "V4": "INSTRUCTION_ACK",
    "BINARY": "BINARY"
}
PROTOCOL_REQ_RESP = ["XT", "VI1", "V4"]

class Packet:
    TEXT_DATA_PREFIX = "2A4851"
    BINARY_DATA_PREFIX = "24"
    def __init__(self, byte_data: bytes):
        self.byte_data = byte_data
        self.hex_data = byte_data.hex().upper()

        if self.hex_data.startswith(self.TEXT_DATA_PREFIX):
            self.is_text = True
        elif self.hex_data.startswith(self.BINARY_DATA_PREFIX):
            self.is_text = False
        else:
            raise ValueError(f"Unknown data type for hex data: {self.hex_data}")

    def get_raw_hex(self):
        return self.hex_data
            
    def decode(self):
        if self.is_text:
            return self.decode_text_data()
        else:
            return self.decode_binary_data()

    def decode_text_data(self):
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

        latitude = float(payload[5][:2]) + float(payload[5][2:]) / 60.0
        if payload[6] == "S": latitude = -latitude

        longitude = float(payload[7][:3]) + float(payload[7][3:]) / 60.0
        if payload[8] == "W": longitude = -longitude

        results = {
            'device_id': payload[1],                                        # Unique device identifier
            'msg_type': payload[2],                                         # Message type (e.g., "V1" for location data) 
            'datetime': datetime_sql,                                       # UTC datetime in SQL format
            'gps_status': payload[4] == 'A',                                # A = valid, V = invalid
            'longitude': longitude,                                         # Longitude in decimal degrees
            'latitude': latitude,                                           # Latitude in decimal degrees
            'speed_kmh': float(payload[9])*1.852,                           # Speed in km/h (converted from knots)
            'heading': int(payload[10]),                                    # Heading in degrees
            'status_hex': payload[12],                                      # Status in hexadecimal format
            'gsm': {
                'mcc': int(payload[13]),                                    # Country code (Poland = 260)
                'mnc': int(payload[14]),                                    # Network code
                'lac': int(payload[15]) if len(payload) > 15 else None,     # Location Area Code (LAC)
                'cell_id': int(payload[16]) if len(payload) > 16 else None  # Cell ID
            }
        }
    
        return results, results['msg_type']

    def decode_binary_data(self):  
        # Ignore binary data. TODO: implement binary data decoding.     
        return None, "BINARY"

    def encode(self):
        self.byte_data = bytes.fromhex(self.hex_data)
        return self.byte_data

    @staticmethod
    def encode_ack_response(device_id: int) -> bytes:
        text = f"*HQ,{device_id},AP00#"
        return text.encode('ascii')

    @staticmethod
    def encode_interval_setting(device_id: int, interval_seconds: int, is_driving: bool) -> bytes:
        mode = "XT" if is_driving else "NXT"
        text = f"*HQ,{device_id},{mode},{interval_seconds}#"
        return text.encode('ascii')

    @staticmethod
    def encode_call_reboot(device_id: int) -> bytes:
        text = f"*HQ,{device_id},CQ#"
        return text.encode('ascii') 

    @staticmethod
    def encode_call_location(device_id: int) -> bytes:
        text = f"*HQ,{device_id},CR#"
        return text.encode('ascii')