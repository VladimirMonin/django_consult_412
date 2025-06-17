Сделали 2 кастомные команды:

python manage.py setup_project
python manage.py create_admin_group

Для линукса 
python3 manage.py setup_project && python3 manage.py create_admin_group

python3 manage.py migrate && echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'ad@ad.com', '12345')" | python3 manage.py shell