from datetime import datetime
from server import Server, logging
import signal

if __name__ == "__main__":
    HOST = "0.0.0.0" 
    PORT = 5023
    
    LOG_NAME = datetime.now().strftime("%Y%m%d_%H%M%S") + ".log"
    logging.basicConfig(filename=LOG_NAME, encoding='utf-8', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    server = Server(host=HOST, port=PORT, db_name=LOG_NAME.split('.')[0] + ".db")

    def _handle_shutdown(signum, _frame):
        server.stop()

    signal.signal(signal.SIGTERM, _handle_shutdown)
    signal.signal(signal.SIGINT, _handle_shutdown)

    server.run()