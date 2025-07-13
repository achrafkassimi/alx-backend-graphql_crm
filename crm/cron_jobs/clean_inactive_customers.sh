#!/bin/bash

# Get the current date and time for the timestamp
timestamp=$(date "+%Y-%m-%d %H:%M:%S")

# Run the Django command to clean up inactive customers
deleted_customers=$(python3 manage.py shell -c "from crm.models import Customer; from datetime import datetime, timedelta; inactive_date = datetime.now() - timedelta(days=365); customers_to_delete = Customer.objects.filter(last_order__lt=inactive_date); deleted = customers_to_delete.delete(); print(deleted[0])")

# Log the number of deleted customers along with the timestamp
echo "$timestamp - Deleted $deleted_customers customers" >> /tmp/customer_cleanup_log.txt
