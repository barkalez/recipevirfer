# recipes_project

Base de proyecto para recetas con Django + Django REST Framework + frontend Django (templates/static), preparado para escalar.

## Resumen de lo implementado
- Proyecto Django con configuración por entornos:
  - `config/settings/base.py`
  - `config/settings/dev.py`
  - `config/settings/prod.py`
- API base con prefijo `/api/v1/`.
- Endpoint de salud:
  - `GET /api/v1/health/` -> `{"status": "ok"}`
- Landing visual animada en `/` y home en `/home/`.
- Home con accesos a:
  - `/ingredients/new/`
  - `/recipes/new/`
  - `/weekly-menu/create/`
- Formularios funcionales conectados a base de datos para:
  - Ingredientes
  - Recetas
  - Menú semanal
- Formulario de ingrediente en versión esencial y organizado por secciones:
  - General
  - Nutricion
  - Dieta
  - Cocina
  - Conservacion y Compra
- Mensajes de confirmación visual y animaciones de interfaz.

## Base de datos usada
Se usa **PostgreSQL** mediante `DATABASE_URL` (django-environ).

Ejemplo en `.env`:
```env
DATABASE_URL=postgres:///recipes_db
```

Notas:
- El proyecto no hardcodea credenciales.
- En desarrollo se puede usar instancia local de PostgreSQL (Termux/Linux/macOS).

## Estructura del proyecto
```text
recipes_project/
├── manage.py
├── README.md
├── requirements.txt
├── .env.example
├── config/
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
│   └── settings/
│       ├── base.py
│       ├── dev.py
│       └── prod.py
├── apps/
│   └── recipes/
│       ├── api/
│       │   ├── urls.py
│       │   └── views.py
│       ├── web/
│       │   ├── forms.py
│       │   ├── urls.py
│       │   ├── views.py
│       │   ├── templates/
│       │   │   ├── landing.html
│       │   │   ├── home.html
│       │   │   ├── ingredient_form.html
│       │   │   └── entity_form.html
│       │   └── static/
│       │       ├── css/landing.css
│       │       └── js/landing.js
│       ├── models/
│       │   └── __init__.py
│       └── migrations/
│           ├── 0001_initial.py
│           ├── 0002_ingredient_allergen_info_and_more.py
│           └── 0003_alter_ingredient_options_and_more.py
└── static/
```

## Instalación
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

## Crear superusuario
```bash
python manage.py createsuperuser
```

## Ejecutar servidor
```bash
python manage.py runserver
```

## URLs principales
- Landing: `http://127.0.0.1:8000/`
- Home: `http://127.0.0.1:8000/home/`
- Ingredientes: `http://127.0.0.1:8000/ingredients/new/`
- Recetas: `http://127.0.0.1:8000/recipes/new/`
- Menú semanal: `http://127.0.0.1:8000/weekly-menu/create/`
- Health check API: `http://127.0.0.1:8000/api/v1/health/`
