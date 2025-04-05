set -o errexist
pip install -r requirements.txt
python manage.py collectstactic --no-input
python manage.py migrate

