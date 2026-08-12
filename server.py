# Simulated tracking device (transmitter)

from comm_utils.packet import Packet, PROTOCOL_TYPES, PROTOCOL_REQ_RESP
from comm_utils.socket_connection import SocketConnectionServer
import sql_utils.sql_server as sql
from datetime import datetime
from queue import Empty
import threading
import logging

logger = logging.getLogger(__name__)

class Server:
    def __init__(self, host: str, port: int, db_name: str):

        # Start database
        self.database_name = db_name
        sql.init_database(self.database_name)

        # Start socket server
        self.socket = SocketConnectionServer(host=host, port=port)
        self.socket_thread = threading.Thread(target=self.socket.start, daemon=True)
        self.socket_thread.start()

        # Running flag to allow clean shutdown
        self._stop_event = threading.Event()

    def stop(self):
        """
        Request graceful shutdown of the server loop.
        """
        self._stop_event.set()

    def export_database(self, export_path: str):
        """
        Export the database to a specified path.
        """
        sql.export_database(self.database_name, export_path)
        
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
            if protocol_type in PROTOCOL_TYPES.keys():
                logger.info(f"Received {PROTOCOL_TYPES[protocol_type]} packet from {data_dict['address']}: {packet_data}")
                if packet_data is not None:
                    # Insert GPS trace into the database
                    sql.insert_device(
                        database_name=self.database_name,
                        id=packet_data['device_id'],
                        ip=data_dict['address'][0],
                        gps_status=packet_data['gps_status'],
                        last_datetime=packet_data['datetime']
                    )
                    sql.insert_gps_trace(
                        database_name=self.database_name,
                        device_id=packet_data['device_id'],
                        latitude=packet_data['latitude'],
                        longitude=packet_data['longitude'],
                        datetime_str=packet_data['datetime']
                    )
                # Respond to the HT packet
                if protocol_type in PROTOCOL_REQ_RESP:
                    response = Packet.encode_ack_response(device_id=packet_data['device_id'])
                    self.socket.send_to(data_dict['address'], response)
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
            self.stop()
        finally:
            logger.info("Server is shutting down...")
            self.socket.close()
            self.export_database(self.database_name.split('.')[0] + "_export.json") # Debug: Export database on shutdown TODO: remove in prod