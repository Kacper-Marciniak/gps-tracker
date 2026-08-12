# Simulated tracking device (transmitter)

from comm_utils.packet import Packet, ProtocolType
from comm_utils.socket_connection import SocketConnectionServer
import sql_utils.sql_server as sql
from datetime import datetime
from queue import Empty
import threading
import logging

logger = logging.getLogger("Server")

from datetime import datetime
import logging
log_name = datetime.now().strftime("%Y%m%d_%H%M%S") + ".log"
logging.basicConfig(filename=log_name, encoding='utf-8', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

class Server:
    def __init__(self, host: str, port: int):

        # Start database
        self.database_name = log_name.split('.')[0] + ".db"
        sql.init_database(self.database_name)

        # Start socket server
        self.socket = SocketConnectionServer(host=host, port=port)
        self.socket_thread = threading.Thread(target=self.socket.start, daemon=True)
        self.socket_thread.start()

        # Running flag to allow clean shutdown
        self._stop_event = threading.Event()

    def export_database(self, export_path: str):
        """
        Export the database to a specified path.
        """
        sql.export_database(self.database_name, export_path)
        logger.info(f"Database exported to {export_path}")

    def tick(self):
        """
        Main loop to process incoming data from the socket server.
        """

        # Catch data from the socket server's queue
        try:
            data_dict = self.socket.data_queue.get(timeout=1)
        except Empty:
            return

        try:
            packet_data, protocol_type = Packet(data_dict['data']).decode()

            if protocol_type == ProtocolType.LOGIN:
                logger.info(f"Received LOGIN packet from {data_dict['address']}: {packet_data}")
                # Respond to the login packet
                response = Packet.encode_login_response(device_id=packet_data['device_id'])
                self.socket.send_to(data_dict['address'], response)
                # Insert device data into the database
                sql.insert_device(
                    database_name=self.database_name,
                    id=packet_data['device_id'],
                    ip=data_dict['address'][0],
                    gps_status=packet_data['gps_status'],
                    last_login_datetime=packet_data['datetime']
                )
            elif protocol_type == ProtocolType.TELEMETRY:
                logger.info(f"Received GPRS packet from {data_dict['address']}: {packet_data}")
                # Insert GPS trace into the database
                sql.insert_gps_trace(
                    database_name=self.database_name,
                    device_id=packet_data['device_id'],
                    latitude=packet_data['latitude'],
                    longitude=packet_data['longitude'],
                    datetime_str=packet_data['datetime']
                )
            else:
                raise ValueError(f"Unknown protocol type: {protocol_type}")

        except (ValueError, KeyError, sql.sqlite3.Error) as e:
            logger.error(f"Error processing packet from {data_dict['address']}: {e}")

    def run(self):
        """
        Run the server indefinitely, processing incoming data.
        """
        logger.info("Server is running...")
        try:
            while not self._stop_event.is_set():
                self.tick()
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received, shutting down...")
            self._stop_event.set()
        finally:
            logger.info("Server is shutting down...")
            self.socket.close()
            self.export_database(self.database_name.split('.')[0] + "_export.json") # Debug: Export database on shutdown TODO: remove in prod

if __name__ == "__main__":
    HOST = "0.0.0.0" 
    PORT = 5023
    server = Server(host=HOST, port=PORT)
    server.run()