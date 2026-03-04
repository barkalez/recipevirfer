# recipes_project

Base project with Django + Django REST Framework + PostgreSQL (via `DATABASE_URL`) and split settings for environments.

## Stack
- Django
- Django REST Framework
- PostgreSQL via `psycopg` (psycopg3)
- `django-environ`
- `django-cors-headers`

## Project structure
- `config/`: project config (`settings`, `urls`, `asgi`, `wsgi`)
- `apps/recipes/`: recipes domain base app
  - `api/`: serializers, views, urls
  - `web/`: Django web views and urls
  - `models/`, `services/`, `selectors/`, `tests/`: ready for growth

## Setup
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Database and migrations
Set `DATABASE_URL` in `.env` to your PostgreSQL instance, then run:

```bash
python manage.py migrate
```

## Create superuser
```bash
python manage.py createsuperuser
```

## Run development server
```bash
python manage.py runserver
```

## Health check
- URL: `http://127.0.0.1:8000/api/v1/health/`
- Response: `{ "status": "ok" }`
