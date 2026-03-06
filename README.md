# recipevirfer

Proyecto Django + DRF para gestionar ingredientes nutricionales con arquitectura **local-first** y creación de recetas por **pasos culinarios**.

## Estado actual

- El dataset principal es `csv/nutritional-info.csv`.
- PostgreSQL es la fuente primaria de datos.
- El autocomplete siempre consulta primero la base local.
- USDA FoodData Central se usa solo bajo demanda para ingredientes no existentes.
- La pantalla de crear recetas trabaja con pasos tipo:
  - `Sofreír 2 dientes de ajo picado durante 2 minutos.`

## Arquitectura Local-First

1. Usuario escribe en un autocomplete.
2. Backend consulta PostgreSQL.
3. Si hay coincidencias: devuelve máximo 5.
4. Si no hay coincidencias:
   - Ingredientes: botón `Añadir "..." desde API` (USDA).
   - Medidas, acciones y participios: botón para alta manual local.
5. Una vez importado/creado, el dato queda persistido y aparece en búsquedas futuras locales.

## Modelos principales

### `NutritionalInfoIngredient`
- `source_id` (id local de referencia)
- `fdc_id` (id USDA opcional)
- `name` (nombre visible ES)
- `normalized_name`
- `scientific_name`
- `source_name_en`
- `source` (`csv_import` / `usda_api`)
- `edible_portion`
- `energy_total`
- `protein_total`
- `nutrients` (JSON)
- `source_payload` (JSON técnico)

### `IngredientSearchAlias`
Resolución ES -> EN para USDA.

### `CulinaryUnit`
Medidas culinarias locales (seed/manual).

### `CulinaryAction`
Acciones culinarias locales (seed/manual).

### `CulinaryParticiple`
Participios culinarios locales (seed/manual), para frases tipo `ajo picado`.

## Flujo USDA (solo bajo demanda)

Endpoint: `POST /ingredients/import-from-api/`

- Si el ingrediente ya existe localmente, no consulta USDA.
- Si no existe:
  - resuelve término en español,
  - consulta USDA,
  - selecciona el mejor candidato,
  - mapea nutrientes al esquema local,
  - guarda en PostgreSQL.

## Autocompletes activos

- Ingredientes: `GET /ingredients/suggestions/?q=...`
- Medidas culinarias: `GET /culinary-units/suggestions/?q=...`
- Acciones culinarias: `GET /culinary-actions/suggestions/?q=...`
- Participios culinarios: `GET /culinary-participles/suggestions/?q=...`

Todos:
- máximo 5 resultados,
- búsqueda case-insensitive,
- prioridad por prefijo,
- sin recarga de página,
- navegación con teclado.

## Endpoints de alta manual

- Medidas: `POST /culinary-units/add/`
- Acciones: `POST /culinary-actions/add/`
- Participios: `POST /culinary-participles/add/`

## Página de creación de recetas

Ruta: `/recipes/create/`

Panel **Añadir pasos a la receta** con campos:
1. Acción culinaria
2. Cantidad
3. Unidad
4. Ingrediente
5. Participio
6. Duración (`sg`, `minutos`, `horas`)

Al añadir, se crea una card en **Pasos de la receta añadidos** con texto natural.

- Botón de card: `Eliminar paso`.
- Lógica singular/plural aplicada para unidades y duración.
- Límite de cantidad: máximo `10000`.

## Variables de entorno

Configurar en `.env`:

```env
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost,testserver
DATABASE_URL=postgres://fer@/recipes_db?host=/home/fer/proyectos/python/recipevirfer/.pgdata&port=55432
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
USDA_API_KEY=tu_api_key_usda
USDA_API_BASE_URL=https://api.nal.usda.gov/fdc/v1
```

## Comandos de gestión

```bash
python manage.py migrate
python manage.py purge_usda_ingredient_data
python manage.py import_nutritional_info
python manage.py import_culinary_units --path medidas_culinarias/medidas_culinarias.md
python manage.py import_culinary_actions --path acciones_culinarias/acciones_culinarias.md
python manage.py import_culinary_participles
python manage.py runserver
```

## Verificación rápida

```bash
python manage.py check
python manage.py test apps.recipes.tests
```

Flujo manual recomendado:

1. Ir a `/recipes/create/`.
2. Buscar acción/ingrediente/unidad/participio y seleccionar sugerencias.
3. Si no existe unidad/acción/participio, usar botón de alta local.
4. Si no existe ingrediente, usar `Añadir "..." desde API`.
5. Añadir paso y comprobar frase final en el panel de pasos.

## Notas

- El proyecto está optimizado para minimizar llamadas a USDA (cache local persistente).
- USDA no participa en autocomplete en tiempo real.
