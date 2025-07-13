# crm/cron.py

import logging
from datetime import datetime
import requests

# Set up logging
logging.basicConfig(filename='/tmp/crm_heartbeat_log.txt', level=logging.INFO)

def log_crm_heartbeat():
    # Get the current timestamp
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    # Log the heartbeat message
    logging.info(f"{timestamp} - CRM is alive")

    # Optional: Check GraphQL endpoint
    try:
        response = requests.get('http://localhost:8000/graphql?query={hello}')
        if response.status_code == 200:
            logging.info(f"{timestamp} - GraphQL endpoint is responsive")
        else:
            logging.error(f"{timestamp} - GraphQL endpoint is not responsive")
    except Exception as e:
        logging.error(f"{timestamp} - Error checking GraphQL endpoint: {e}")
