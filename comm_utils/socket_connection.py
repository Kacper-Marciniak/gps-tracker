import socket
import threading
from queue import Queue
import logging

logger = logging.getLogger(__name__)

class SocketConnectionServer:
    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 5000
    ):
        self.host = host
        self.port = port
        self.data_queue = Queue()

        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )
        self.socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        self.running = False

        # Active client connections
        self.clients = {}
        self.clients_lock = threading.Lock()

    def start(self):
        """Start the server and wait for multiple client connections."""

        self.running = True

        self.socket.bind((self.host, self.port))
        self.socket.listen()

        logger.info(f"Socket server started on {self.host}:{self.port}")

        try:
            while self.running:
                conn, addr = self.socket.accept()

                logger.info(f"New client connected: {addr}")

                with self.clients_lock:
                    self.clients[addr] = conn

                # Separate receiver thread for every client
                thread = threading.Thread(
                    target=self._receive_loop,
                    args=(conn, addr),
                    daemon=True
                )

                thread.start()

        except OSError:
            # Expected when the listening socket is closed
            pass

    def _receive_loop(self, conn, addr):
        """Receive raw bytes from a single client."""

        try:
            while self.running:
                data = conn.recv(1024)

                if not data:
                    break
                
                self.data_queue.put({
                    "address": addr,
                    "data": data
                })
                logger.info(f"Received data from {addr}: {data.hex().upper()}")

        except (ConnectionResetError, BrokenPipeError, OSError):
            pass

        finally:
            self._remove_client(conn, addr)

    def _remove_client(self, conn, addr):
        """Remove and close a disconnected client."""

        with self.clients_lock:
            self.clients.pop(addr, None)

        try:
            conn.close()
        except OSError:
            pass

        logger.info(f"Client disconnected: {addr}")

    def send(self, data: bytes):
        """
        Send raw bytes to all currently connected clients.
        """

        if not isinstance(data, bytes):
            raise TypeError(
                "Wrong data type! The send method only accepts bytes objects."
            )

        with self.clients_lock:
            clients = list(self.clients.items())

        for addr, conn in clients:
            try:
                conn.sendall(data)
                logger.info(f"Sent data to {addr}: {data.hex().upper()}")
            except (ConnectionResetError, BrokenPipeError, OSError):
                logger.error(f"Failed to send data to {addr}.")
                self._remove_client(conn, addr)

    def send_to(self, addr, data: bytes):
        """Send raw bytes to a specific client."""

        if not isinstance(data, bytes):
            raise TypeError(
                "Wrong data type! The send method only accepts bytes objects."
            )

        with self.clients_lock:
            conn = self.clients.get(addr)

        if conn is None:
            logger.error(f"Failed to send data to {addr}.")
            return

        try:
            conn.sendall(data)
            logger.info(f"Sent data to {addr}: {data.hex().upper()}")
        except (ConnectionResetError, BrokenPipeError, OSError):
            logger.error(f"Failed to send data to {addr}.")
            self._remove_client(conn, addr)

    def close(self):
        """Stop the server and close all connections."""

        self.running = False

        # Close listening socket
        try:
            self.socket.close()
        except OSError:
            pass

        # Close all clients
        with self.clients_lock:
            clients = list(self.clients.items())
            self.clients.clear()

        for addr, conn in clients:
            try:
                conn.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

            try:
                conn.close()
            except OSError:
                pass

        logger.info(f"Socket server on {self.host}:{self.port} has been closed.")

    def __del__(self):
        self.close()