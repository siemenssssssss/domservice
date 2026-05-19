#!/bin/bash
pip install -r requirements.txt
python manage.py migrate
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None"
python manage.py create_default_services
python manage.py create_default_news
python manage.py create_default_documents
python manage.py create_test_users