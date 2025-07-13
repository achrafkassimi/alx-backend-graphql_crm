# Understanding GraphQL

python manage.py makemigrations
python manage.py migrate
python manage.py runserver

Create crm/README.md with steps to:

InstallRedis and dependencies.
Run migrations (python manage.py migrate).
Start Celery worker (celery -A crm worker -l info).
Start Celery Beat (celery -A crm beat -l info).
Verify logs in /tmp/crm_report_log.txt.