# crm/cron_jobs/send_order_reminders.py

import logging
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Set up logging
logging.basicConfig(filename='/tmp/order_reminders_log.txt', level=logging.INFO)

# GraphQL client setup
transport = RequestsHTTPTransport(
    url='http://localhost:8000/graphql',
    use_json=True,
)

client = Client(transport=transport, fetch_schema_from_transport=True)

def fetch_pending_orders():
    # Calculate the date for one week ago
    one_week_ago = datetime.now() - timedelta(days=7)
    formatted_date = one_week_ago.strftime('%Y-%m-%d')

    # Define the GraphQL query
    query = gql('''
    query getPendingOrders($date: String!) {
        orders(order_date: $date) {
            id
            customer {
                email
            }
        }
    }
    ''')

    # Execute the query
    result = client.execute(query, variable_values={"date": formatted_date})
    return result['orders']

def log_order_reminders(orders):
    for order in orders:
        order_id = order['id']
        customer_email = order['customer']['email']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logging.info(f"{timestamp} - Order ID: {order_id}, Customer Email: {customer_email}")

def main():
    orders = fetch_pending_orders()
    log_order_reminders(orders)
    print("Order reminders processed!")

if __name__ == "__main__":
    main()
