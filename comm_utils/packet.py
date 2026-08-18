# Protocol packet format
from enum import Enum
from datetime import datetime, timezone

PROTOCOL_TYPES = {
    "V1": "LOCATION_DATA",
    "XT": "HEARTBEAT",
    "VI1": "LOCATION_REQUEST",
    "V4": "INSTRUCTION_ACK",
    "BINARY": "LOCATION_DATA_BINARY",
}
PROTOCOL_IGNORE = []
PROTOCOL_REQ_RESP = ["V1", "XT", "VI1", "V4"]
PROTOCOL_DEVICE_UPDATE = ["V1", "BINARY"]
PROTOCOL_ADD_TRACE = ["V1", "BINARY"]

DIRECTION_MAP = {
    0x00: "N",
    0x01: "S",
    0x02: "W",
    0x03: "E",
    0x04: "NE",
    0x05: "SE",
    0x06: "SW",
    0x07: "NW",
    0x0E: "E",
}

def get_time():
    return datetime.now(timezone.utc).strftime("%H%M%S")

def get_date():
    return datetime.now(timezone.utc).strftime("%d%m%y")

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
            },
            'heartbeat': True
        }
    
        return results, results['msg_type']

    def decode_binary_data(self):

        payload = self.byte_data

        if len(payload) < 45:
            return None, "BINARY"

        def bcd_byte(value):
            return ((value >> 4) * 10) + (value & 0x0F)

        def bcd_bytes(data):
            return "".join(f"{bcd_byte(byte):02d}" for byte in data)

        device_id = bcd_bytes(payload[1:6])

        hour = bcd_byte(payload[6])
        minute = bcd_byte(payload[7])
        second = bcd_byte(payload[8])

        day = bcd_byte(payload[9])
        month = bcd_byte(payload[10])
        year = 2000 + bcd_byte(payload[11])

        datetime_sql = datetime(year,month,day,hour,minute,second,)

        datetime_sql = datetime_sql.strftime("%Y-%m-%d %H:%M:%S")

        battery = payload[16]

        latitude = f"{payload[12]:02X}{payload[13]:02X}{payload[14]:02X}{payload[15]:02X}"
        longitude = f"{payload[17]:02X}{payload[18]:02X}{payload[19]:02X}{payload[20]:02X}"
        latitude = int(latitude[:2])+int(latitude[2:])/10000/60.
        longitude = int(longitude[:3])+int(longitude[3:])/1000./60.

        direction_nibble = payload[21] & 0x0F

        longitude_direction = DIRECTION_MAP.get(direction_nibble)

        speed_and_direction = f"{payload[22]:02X}{payload[23]:02X}{payload[24]:02X}"
        speed_kmh = float(int(speed_and_direction[:3])) * 1.852
        heading = int(speed_and_direction[3:])        

        status_hex = payload[25:29].hex().upper()

        user_alarm = payload[29]
        gsm_raw = payload[30]

        signal_raw = payload[31:33].hex().upper()

        mileage = int.from_bytes(
            payload[33:37],
            byteorder="big",
            signed=False,
        )

        mcc = int.from_bytes(
            payload[37:39],
            byteorder="big",
            signed=False,
        )

        mnc = payload[39]

        lac = int.from_bytes(
            payload[40:42],
            byteorder="big",
            signed=False,
        )

        cell_id = int.from_bytes(
            payload[42:44],
            byteorder="big",
            signed=False,
        )

        record_number = payload[44]

        results = {
            "device_id": device_id,
            "msg_type": "BINARY",
            "datetime": datetime_sql,
            "gps_status": True,
            "longitude": longitude,
            "latitude": latitude,
            "speed_kmh": speed_kmh,
            "heading": heading,
            "status_hex": status_hex,
            "gsm": {
                "mcc": mcc,
                "mnc": mnc,
                "lac": lac,
                "cell_id": cell_id,
            },
            "battery": battery,
            "longitude_direction": longitude_direction,
            "user_alarm": user_alarm,
            "gsm_raw": gsm_raw,
            "signal_raw": signal_raw,
            "mileage": mileage,
            "record_number": record_number,
            "heartbeat": False
        }

        return results, "BINARY"

    def encode(self):
        self.byte_data = bytes.fromhex(self.hex_data)
        return self.byte_data

    @staticmethod
    def encode_ack_response(device_id: int) -> bytes:
        text = f"*HQ,{device_id},AP00,{get_time()}#"
        return text.encode('ascii')

    @staticmethod
    def encode_interval_setting(device_id: int, interval_seconds: int, is_driving: bool) -> bytes:
        mode = "XT" if is_driving else "NXT"
        text = f"*HQ,{device_id},{mode},{interval_seconds},{get_time()}#"
        return text.encode('ascii')

    @staticmethod
    def encode_call_reboot(device_id: int) -> bytes:
        text = f"*HQ,{device_id},CQ,{get_time()}#"
        return text.encode('ascii') 

    @staticmethod
    def encode_call_location(device_id: int) -> bytes:
        text = f"*HQ,{device_id},CR,{get_time()}#"
        return text.encode('ascii')