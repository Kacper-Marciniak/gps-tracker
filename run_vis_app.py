from app.app import app, logger
from app.integration.names import DATABASE_NAME, LOG_NAME, SERVER_LOG_NAME

import logging

if __name__ == "__main__":    

    logging.basicConfig(filename=LOG_NAME, encoding='utf-8', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    try:
        logging.info(f"Starting Dash app with database: {DATABASE_NAME} and log file: {SERVER_LOG_NAME}")
        app.run(
            host="0.0.0.0",
            port=8080,
            debug=False
        )
    except Exception as e:
        logger.error(f"Error running the Dash app: {e}")