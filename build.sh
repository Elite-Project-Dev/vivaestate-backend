set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Apply migrations
python manage.py migrate --noinput

# Optionally create a superuser (only if needed)
python manage.py createsuperuser --noinput || true

