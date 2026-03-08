# recipevirfer

Proyecto Django + DRF para gestionar ingredientes nutricionales con enfoque local-first y creación de recetas por pasos culinarios.
Incluye autenticación web con sesiones (Django auth + django-allauth) y usuario personalizado.

## Resumen funcional

- Dataset base: `csv/nutritional-info.csv`.
- PostgreSQL es la fuente primaria de datos.
- Autenticación web profesional con registro/login/logout, verificación de email y recuperación de contraseña.
- Los autocompletes consultan primero la base local.
- USDA FoodData Central se consulta solo bajo demanda para ingredientes no existentes.
- La pantalla de recetas construye frases como: `Sofreir 2 dientes de ajo picado durante 2 minutos.`

## Requisitos

- Python 3.9+
- PostgreSQL accesible desde `DATABASE_URL`
- `pip` y entorno virtual (`venv`)

## Quickstart

1. Crear y activar entorno virtual.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Instalar dependencias.

```bash
pip install -r requirements.txt
```

3. Crear `.env` a partir del ejemplo y ajustarlo.

```bash
cp .env.example .env
```

4. Aplicar migraciones.

```bash
python manage.py migrate
```

5. Cargar datos iniciales recomendados.

```bash
python manage.py import_nutritional_info
python manage.py import_culinary_units --path medidas_culinarias/medidas_culinarias.md
python manage.py import_culinary_actions --path acciones_culinarias/acciones_culinarias.md
python manage.py import_culinary_participles
```

Alternativa reproducible (usando fixture versionado en Git):

```bash
python manage.py loaddata apps/recipes/fixtures/initial_seed_data.json
```

6. Crear superusuario (opcional para admin).

```bash
python manage.py createsuperuser
```

7. Arrancar servidor de desarrollo.

```bash
python manage.py runserver
```

## Variables de entorno

Ejemplo base (`.env`):

```env
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost,testserver
DATABASE_URL=postgres://fer@/recipes_db?host=/home/fer/proyectos/python/recipevirfer/.pgdata&port=55432
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
USDA_API_KEY=DEMO_KEY
USDA_API_BASE_URL=https://api.nal.usda.gov/fdc/v1
DEFAULT_FROM_EMAIL=no-reply@recipevirfer.local
```

Nota: valida la ruta del `host` Unix socket en `DATABASE_URL` para tu entorno local.

## Arquitectura local-first

1. El usuario escribe en un autocomplete.
2. El backend consulta PostgreSQL.
3. Si hay coincidencias, devuelve maximo 5.
4. Si no hay coincidencias:
- Ingredientes: boton `Anadir "..." desde API` (USDA).
- Medidas, acciones y participios: alta manual local.
5. Una vez importado/creado, el dato queda persistido para futuras busquedas locales.

## Modelos principales

### `NutritionalInfoIngredient`

- `source_id` (id local de referencia)
- `fdc_id` (id USDA opcional)
- `name`
- `normalized_name`
- `scientific_name`
- `source_name_en`
- `source` (`csv_import` / `usda_api`)
- `edible_portion`
- `energy_total`
- `protein_total`
- `nutrients` (JSON)
- `source_payload` (JSON tecnico)

### `IngredientSearchAlias`

Resolucion ES -> EN para USDA.

### `CulinaryUnit`

Medidas culinarias locales (seed/manual).

### `CulinaryAction`

Acciones culinarias locales (seed/manual).

### `CulinaryParticiple`

Participios culinarios locales (seed/manual), para frases tipo `ajo picado`.

### `CulinaryTemperature`

Temperaturas culinarias locales persistentes (seed/manual), para frases tipo `a 180 ºC`.

### `accounts.User` (custom user model)

- `email` unico (identificador principal de login)
- `display_name`
- `first_name`, `last_name`
- `is_active`, `is_staff`, `date_joined`

## Endpoints web

- `GET /` landing
- `GET /home/`
- `GET /ingredients/`
- `GET /ingredients/<source_id>/`
- `GET /ingredients/<source_id>/json/`
- `GET /recipes/create/`
- `GET /recipes/<id>/`
- `GET /recipes/<id>/edit/`
- `POST /recipes/save/`
- `POST /recipes/<id>/update/`

### Autocompletes

- `GET /ingredients/suggestions/?q=...`
- `GET /culinary-units/suggestions/?q=...`
- `GET /culinary-actions/suggestions/?q=...`
- `GET /culinary-participles/suggestions/?q=...`
- `GET /culinary-temperatures/suggestions/?q=...`

Todos devuelven maximo 5 resultados, con busqueda case-insensitive y prioridad por prefijo.

### Altas manuales

- `POST /culinary-units/add/`
- `POST /culinary-actions/add/`
- `POST /culinary-participles/add/`
- `POST /culinary-temperatures/add/`

### Importacion USDA bajo demanda

- `POST /ingredients/import-from-api/`

Comportamiento:
- Si el ingrediente ya existe localmente, no consulta USDA.
- Si no existe, consulta USDA, mapea nutrientes y persiste en PostgreSQL.

## Endpoints API (DRF)

Prefijo: `/api/v1/`

- `GET /api/v1/health/`
- `GET /api/v1/ingredients/`
- `GET /api/v1/ingredients/<source_id>/`

## Flujo de creacion de recetas

Ruta: `/recipes/create/`

Importante: para crear/guardar/editar/ver detalle de recetas hay que iniciar sesión.
Cada receta nueva se guarda asociada al usuario autenticado (`Recipe.owner`).

Campos del paso culinario:
1. Accion culinaria
2. Cantidad
3. Unidad
4. Ingrediente
5. Participio
6. Temperatura (opcional)
7. Duracion (`sg`, `minutos`, `horas`, opcional)

Al anadir un paso, se genera una card en "Pasos de la receta anadidos" con texto natural.

- Incluye boton `Eliminar paso`.
- Aplica logica singular/plural para unidades y duracion.
- Limite de cantidad: `10000`.

## Autenticación web (allauth)

Rutas principales:

- `/accounts/login/`
- `/accounts/signup/`
- `/accounts/logout/`
- `/accounts/password/change/`
- `/accounts/password/reset/`
- `/accounts/confirm-email/` (flujo allauth)
- `/accounts/profile/` y `/accounts/` (zona de cuenta)

Login principal por email+password.
La verificación de email y reset de contraseña se prueban en local con backend de correo a consola.

## Comandos utiles

```bash
python manage.py check
python manage.py test apps.accounts.tests apps.recipes.tests
python manage.py test apps.recipes.tests
python manage.py purge_usda_ingredient_data
```

## OpenNutrition: carga completa y traduccion al vuelo

### Cargar todo el dataset raw (ingles) en PostgreSQL

El importador `import_opennutrition_raw` carga el TSV completo sin traducir masivamente.

```bash
python manage.py import_opennutrition_raw --path opennutrition_dataset/opennutrition_foods.tsv --batch-size 5000
```

Resultado esperado con el archivo actual:
- filas procesadas: `326759`
- ingredientes `opennutrition_raw` en BD: `326759`

Nota tecnica:
- el importador aplica truncado seguro en campos `CharField` limitados para evitar errores `varchar(300)` al cargar nombres largos.

### Traduccion on-demand al seleccionar ingrediente

En `/recipes/create/` la traduccion se dispara al seleccionar un ingrediente OpenNutrition:

1. Si ya esta traducido correctamente, se reutiliza.
2. Si esta en ingles o pendiente:
   - intenta con LibreTranslate local (`LIBRETRANSLATE_URL`)
   - si falla/no traduce, usa fallback local EN->ES para terminos comunes
   - si sigue sin traducir, aplica fallback online (MyMemory) para resolver casos como `Watermelon -> Sandia`
3. Guarda el resultado en BD para reutilizacion futura.

Ademas, si un registro quedo marcado como `translated` pero con texto ingles (estado historico inconsistente), el sistema ahora lo repara automaticamente al volver a seleccionarlo.

## UI nutricional (ingredientes)

- Listado de ingredientes redisenado con cards y resumen nutricional rapido:
  - `Calories`, `Protein`, `Carbohydrates`, `Fat`, `Fiber`
  - card completa clicable hacia detalle
- Vista individual de ingrediente:
  - secciones por categoria (`Carbs`, `Fat`, `Protein`, `Amino Acids`, `Vitamins`, `Minerals`, `Other`)
  - se muestran tambien nutrientes en `0`
  - layout optimizado para evitar huecos vacios
  - estilo visual unificado en tema oscuro

## Preparado para JWT en API

La web usa sesiones de Django como flujo principal.
La API DRF mantiene separación para que más adelante puedas añadir Simple JWT en `/api/v1/auth/` sin romper login web.

## Persistencia en otras maquinas (GitHub)

El estado de PostgreSQL no viaja con `git push`. Para mantener datos iniciales entre maquinas:

1. Se versiona el fixture `apps/recipes/fixtures/initial_seed_data.json`.
2. En la nueva maquina, tras `pull`, ejecutar:

```bash
python manage.py migrate
python manage.py loaddata apps/recipes/fixtures/initial_seed_data.json
```

Si anades nuevos ingredientes/unidades/acciones/participios en tu maquina actual, regenera el fixture antes de `git push`:

```bash
python manage.py dumpdata recipes.NutritionalInfoIngredient recipes.CulinaryUnit recipes.CulinaryAction recipes.CulinaryParticiple --indent 2 > apps/recipes/fixtures/initial_seed_data.json
```

Luego haz `git add`, `git commit` y `git push`. En la otra maquina, tras `pull`, aplica `loaddata` para reflejar esos nuevos datos.

## Troubleshooting

- Warning `staticfiles.W004`: crea el directorio `static/` en la raiz del proyecto o ajusta `STATICFILES_DIRS`.
- Si aparecen migraciones pendientes: `python manage.py migrate`.
- Si falla la conexion a base de datos, revisa `DATABASE_URL` y que PostgreSQL este levantado.
- Si ya tenias una BD antigua con `auth.User` y migraste a `accounts.User`, recrea la BD local y ejecuta migraciones desde cero.

## Saneo de BD local (historial de migraciones inconsistente)

Si aparece `InconsistentMigrationHistory`, el codigo puede estar correcto y el problema ser solo local.
Procedimiento limpio aplicado en este proyecto:

```bash
# 1) Backup
mkdir -p backups/db
pg_dump "$DATABASE_URL" > "backups/db/recipes_db_before_reset_$(date +%Y%m%d_%H%M%S).sql"

# 2) Reconectar a la BD postgres administrativa
ADMIN_URL="${DATABASE_URL%/*}/postgres"

# 3) Cerrar conexiones a la BD objetivo (ejemplo recipes_db)
psql "$ADMIN_URL" -v ON_ERROR_STOP=1 -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'recipes_db' AND pid <> pg_backend_pid();"

# 4) Reset de BD
psql "$ADMIN_URL" -v ON_ERROR_STOP=1 -c "DROP DATABASE IF EXISTS \"recipes_db\";"
psql "$ADMIN_URL" -v ON_ERROR_STOP=1 -c "CREATE DATABASE \"recipes_db\";"

# 5) Migraciones + seed
python manage.py migrate --noinput
python manage.py loaddata apps/recipes/fixtures/initial_seed_data.json

# 6) Verificaciones finales
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test apps.accounts.tests
```
