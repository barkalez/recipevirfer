# recipevirfer

Proyecto Django + Django REST Framework para gestionar y consultar un catalogo de ingredientes cargados desde CSV (USDA traducido), con interfaz web basica y API REST.

## Estado actual del dominio
- Modelo principal activo: `CsvIngredient`
  - `fdc_id` (unico)
  - `alimento`
  - `nutrientes` (JSON)
- El flujo manual antiguo (altas de ingredientes/recetas/menu semanal) fue retirado del modelo actual.
- El proyecto hoy esta centrado en:
  - Importacion masiva desde CSV
  - Exploracion web de ingredientes
  - Consulta por API con filtros

## Stack
- Python 3
- Django 6
- Django REST Framework
- PostgreSQL (`DATABASE_URL` via `django-environ`)

## Configuracion de entorno
1. Crear entorno virtual e instalar dependencias:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

2. Crear `.env`:

```bash
cp .env.example .env
```

3. Ajustar variables segun tu entorno:

```env
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=postgres://postgres:postgres@localhost:5432/recipes_db
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Base de datos
Aplicar migraciones:

```bash
python manage.py migrate
```

Opcional (admin):

```bash
python manage.py createsuperuser
```

## Carga de datos CSV
Comando disponible:

```bash
python manage.py import_ingredientes_csv --path /ruta/al/ingredientes_reales_usda_es.csv
```

Opciones:
- `--batch-size 1000` (default)
- `--keep-existing` para no vaciar tabla antes de importar

Requisitos minimos del CSV:
- Columna `fdc_id`
- Columna `alimento` o `food`
- El resto de columnas se guardan dentro de `nutrientes` (JSON)

## Ejecucion local
```bash
python manage.py runserver
```

## Rutas web
- `GET /` landing visual
- `GET /home/` resumen del total cargado
- `GET /ingredients/` listado con buscador y paginacion

## API REST (`/api/v1/`)

### Health
- `GET /api/v1/health/`
- Respuesta:

```json
{"status": "ok"}
```

### Listado de ingredientes
- `GET /api/v1/ingredients/`

Query params soportados:
- `q`: texto para buscar por `alimento` o `fdc_id`
- `categoria`: categoria inferida por palabras clave (`vegetal`, `fruta`, `legumbre`, `cereal`, `proteina_animal`, `lacteo`, `grasa_aceite`, `frutos_secos_semillas`, `especia_hierba`)
- `protein_min`
- `protein_max`
- `calories_min`
- `calories_max`

Ejemplo:

```http
GET /api/v1/ingredients/?q=tomate&categoria=vegetal&protein_min=1&calories_max=50
```

### Detalle por `fdc_id`
- `GET /api/v1/ingredients/<fdc_id>/`

## Estructura relevante
```text
.
├── manage.py
├── requirements.txt
├── .env.example
├── config/
│   ├── urls.py
│   └── settings/
│       ├── base.py
│       ├── dev.py
│       └── prod.py
└── apps/recipes/
    ├── models/__init__.py
    ├── admin.py
    ├── api/
    │   ├── urls.py
    │   ├── views.py
    │   ├── serializers.py
    │   └── category.py
    ├── web/
    │   ├── urls.py
    │   ├── views.py
    │   ├── templates/
    │   └── static/
    └── management/commands/import_ingredientes_csv.py
```

## Notas
- `manage.py` usa por defecto `config.settings.dev`.
- La API usa paginacion por pagina (`PAGE_SIZE=10`).
- Actualmente no hay tests implementados en `apps/recipes/tests/`.
