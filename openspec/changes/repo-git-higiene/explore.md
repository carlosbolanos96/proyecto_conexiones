# Exploracion: repo-git-higiene

## Contexto / Problema

El repositorio esta en una etapa temprana de Django y ya fue empujado a `origin` con un unico commit. La higiene actual de Git mezcla codigo fuente, bytecode, una base SQLite con datos, configuracion sensible y artefactos OpenSpec. Antes de proponer cambios conviene separar hechos verificados de decisiones pendientes, porque algunas acciones implican rotacion de secretos, limpieza de historial o cambios de flujo para multiples desarrolladores.

## Hallazgos Verificados

### A. Inventario Git

Evidencia: `git ls-files` procesado por script Python.

```text
tracked_total 223
source .py: 116
bytecode .pyc: 92
docs/config/templates: 13
other: 1
data/db: 1

extensions:
.html: 1
.json: 1
.md: 11
.py: 116
.pyc: 92
.sqlite3: 1
.yaml: 1
```

Hechos:
- No hay `.gitignore`; 92 de 223 archivos trackeados son `.pyc`.
- `db.sqlite3` esta trackeado.
- `.atl/.skill-registry.cache.json`, `.atl/skill-registry.md` y artefactos `openspec/` tambien estan trackeados.
- `.venv/` existe en disco pero no aparece en `git ls-files`.

### B. Contenido de `db.sqlite3`

Evidencia: inspeccion SQLite limitada a nombres de tablas y conteos, sin volcar filas ni datos personales.

```text
table_count 24
accounts_profile: 12
agro_producer: 3
agro_product: 6
auth_group: 0
auth_group_permissions: 0
auth_permission: 80
auth_user: 13
auth_user_groups: 0
auth_user_user_permissions: 0
delivery_courier: 3
delivery_delivery: 3
django_admin_log: 0
django_content_type: 20
django_migrations: 29
django_session: 3
inventory_inventoryitem: 6
locations_address: 12
menus_restaurantproduct: 6
notifications_notification: 5
orders_order: 6
orders_orderitem: 9
payments_payment: 6
restaurants_restaurant: 3
warehouses_warehouse: 3
```

Evidencia adicional de conteos agregados:

```text
auth_user total: 13
auth_user demo_prefix: 12
auth_user non_demo_prefix: 1
django_session total: 3
```

Lectura prudente:
- La base contiene datos de aplicacion, usuarios y sesiones.
- `core/management/commands/seed_demo.py` define `DEMO_PREFIX = 'demo_'` y crea datos demo; 12 usuarios coinciden con ese prefijo.
- Hay 1 usuario fuera del prefijo demo y 3 sesiones. Sin ver filas, no se puede confirmar si son datos reales de una persona, pero la base no es un archivo vacio ni puramente estructural.

### C. Secretos y Exposicion

Evidencia: escaneo redaccionado de HEAD e historial con patrones para `SECRET_KEY`, asignaciones de secretos/tokens/passwords, AWS keys, GitHub tokens, private keys y URLs con credenciales.

```text
HEAD tree secret scan (redacted)
conexiones/settings.py:23: django_secret_key
core/management/commands/seed_demo.py:79: generic_assignment_secret

History secret scan (redacted)
c82bdb1b0a0a conexiones/settings.py:23: django_secret_key
c82bdb1b0a0a core/management/commands/seed_demo.py:79: generic_assignment_secret
```

Hechos:
- El `SECRET_KEY` esta presente en el arbol actual: `conexiones/settings.py:23`.
- El `SECRET_KEY` esta alcanzable en la historia: commit `c82bdb1b0a0a...`.
- El repositorio tiene un unico commit local y remoto: `c82bdb1 "creating the proyect"`.
- La otra coincidencia es `core/management/commands/seed_demo.py:79`, donde se usa una password fija para usuarios demo. Es credencial demo, no se observo como secreto externo/API token, pero debe tratarse con cuidado si esos usuarios existen en una base compartida.
- No se detectaron otros API keys, tokens, private keys, AWS keys ni URLs con credenciales en archivos trackeados o en el unico commit reachable por `git rev-list --all`.

Evidencia remota:

```text
origin https://github.com/carlosbolanos96/proyecto_conexiones.git (fetch)
origin https://github.com/carlosbolanos96/proyecto_conexiones.git (push)
origin/master c82bdb1
git ls-remote --heads origin => refs/heads/master en c82bdb1...
```

Que se puede y no se puede determinar:
- Se puede verificar que el commit con el secreto esta en `origin/master`.
- Se puede verificar que este clone local solo conoce `origin/master` como remote-tracking ref.
- No se puede determinar desde Git local si alguien mas clono, fork-eo o descargo el repo. Git no conserva esa telemetria en el repositorio local.

### D. Estado de Migraciones

Evidencia: deteccion de apps con `apps.py` y migraciones numeradas.

```text
apps_with_apps_py accounts, agro, core, delivery, inventory, locations, menus, notifications, orders, payments, restaurants, warehouses
accounts: migrations=['0001_initial.py']
agro: migrations=['0001_initial.py']
core: migrations=[]
delivery: migrations=['0001_initial.py']
inventory: migrations=['0001_initial.py']
locations: migrations=['0001_initial.py']
menus: migrations=['0001_initial.py']
notifications: migrations=['0001_initial.py']
orders: migrations=['0001_initial.py']
payments: migrations=['0001_initial.py']
restaurants: migrations=['0001_initial.py']
warehouses: migrations=['0001_initial.py']
```

Hay 12 apps locales, no 13 segun `INSTALLED_APPS` y `apps.py`: `core`, `accounts`, `locations`, `orders`, `payments`, `notifications`, `restaurants`, `menus`, `delivery`, `agro`, `warehouses`, `inventory`.

Evidencia: `.venv/Scripts/python.exe manage.py makemigrations --check --dry-run`.

```text
returncode 1
Migrations for 'locations': locations\migrations\0002_alter_address_options_alter_address_city_and_more.py
Migrations for 'notifications': notifications\migrations\0002_alter_notification_options_and_more.py
Migrations for 'restaurants': restaurants\migrations\0002_alter_restaurant_options_alter_restaurant_address_and_more.py
Migrations for 'accounts': accounts\migrations\0002_alter_profile_options_alter_profile_avatar_and_more.py
Migrations for 'agro': agro\migrations\0002_alter_producer_options_alter_product_options_and_more.py
Migrations for 'menus': menus\migrations\0002_alter_restaurantproduct_options_and_more.py
Migrations for 'orders': orders\migrations\0002_alter_order_options_alter_orderitem_options_and_more.py
Migrations for 'payments': payments\migrations\0002_alter_payment_options_alter_payment_amount_and_more.py
Migrations for 'warehouses': warehouses\migrations\0002_alter_warehouse_options_alter_warehouse_address_and_more.py
Migrations for 'delivery': delivery\migrations\0002_alter_courier_options_alter_delivery_options_and_more.py
Migrations for 'inventory': inventory\migrations\0002_alter_inventoryitem_options_and_more.py
```

Evidencia: `.venv/Scripts/python.exe manage.py showmigrations` y tabla `django_migrations`.

```text
accounts [X] 0001_initial
agro [X] 0001_initial
core (no migrations)
delivery [X] 0001_initial
inventory [X] 0001_initial
locations [X] 0001_initial
menus [X] 0001_initial
notifications [X] 0001_initial
orders [X] 0001_initial
payments [X] 0001_initial
restaurants [X] 0001_initial
warehouses [X] 0001_initial
```

Lectura:
- Las migraciones `0001_initial.py` estan aplicadas en `db.sqlite3`.
- Los modelos actuales no coinciden con esas migraciones; Django quiere generar `0002` para 11 apps.
- Por lo tanto, `db.sqlite3` esta sincronizada con las migraciones existentes, pero no con el estado actual de `models.py`.

### E. Realidad Arquitectonica

Evidencia: archivos leidos directamente.

```text
conexiones/urls.py: incluye solo core.urls y admin.site.urls
core/urls.py: 1 route, path('', views.home, name='home')
accounts/urls.py: 0 routes
orders/urls.py: 0 routes
agro/urls.py: 0 routes
```

Evidencia de rutas por app:

```text
accounts\urls.py: 0 routes
agro\urls.py: 0 routes
conexiones\urls.py: 2 routes
core\urls.py: 1 routes
delivery\urls.py: 0 routes
inventory\urls.py: 0 routes
locations\urls.py: 0 routes
menus\urls.py: 0 routes
notifications\urls.py: 0 routes
orders\urls.py: 0 routes
payments\urls.py: 0 routes
restaurants\urls.py: 0 routes
warehouses\urls.py: 0 routes
```

Evidencia de modelos:

```text
accounts\models.py: ['Profile']
agro\models.py: ['Producer', 'Product']
core\models.py: []
delivery\models.py: ['Courier', 'Delivery']
inventory\models.py: ['InventoryItem']
locations\models.py: ['Address']
menus\models.py: ['RestaurantProduct']
notifications\models.py: ['Notification']
orders\models.py: ['Order', 'OrderItem']
payments\models.py: ['Payment']
restaurants\models.py: ['Restaurant']
warehouses\models.py: ['Warehouse']
```

Lectura:
- No es solo scaffolding: hay modelos de dominio con relaciones cruzadas entre apps.
- La capa HTTP si es casi scaffolding: solo hay home + admin; las apps tienen `urls.py` vacios y views stub salvo `core.views.home`.
- Hay dependencia cruzada real en modelos: `orders` depende de `locations`, `menus`, `agro`; `agro` depende de `accounts` y `locations`; `delivery` depende de `accounts` y `orders`; `inventory` depende de `warehouses` y `agro`.
- No se encontraron archivos `*service*.py` ni `*repository*.py`.
- La unica logica operacional fuerte observada esta en `core/management/commands/seed_demo.py`, usando ORM directo.
- Solo se encontro un template: `core/templates/core/home.html`.

### F. Superficie de Colision Multi-dev

Archivos con alta probabilidad de conflicto:
- `conexiones/settings.py`: todos necesitaran dependencias, apps instaladas, entorno, DB, seguridad y static/media.
- `conexiones/urls.py`: hoy solo incluye `core`; al conectar apps, todos tenderan a agregar `include(...)` ahi.
- Archivos `*/urls.py`: existen pero estan vacios; cada feature tendra que crear rutas.
- `*/models.py`: ya hay relaciones cruzadas; cambios en entidades centrales como `accounts.Profile`, `orders.Order`, `locations.Address`, `agro.Product` impactan a varias apps.
- `*/migrations/`: como los modelos ya estan fuera de sync, multiples desarrolladores generando `0002` en paralelo chocaran casi seguro.
- Futuro manifiesto de dependencias (`requirements.txt` o `pyproject.toml`): no existe todavia y sera editado por todos al instalar paquetes.
- `.gitignore`: tampoco existe y sera un cambio transversal necesario antes de limpiar `.pyc`/DB.

Perfil realista de conflictos:
- Conflictos de migraciones `0002_*` por nombres duplicados y dependencias cruzadas.
- Conflictos simples pero frecuentes en `settings.py` y `conexiones/urls.py`.
- Riesgo de drift local si cada persona usa su propio `db.sqlite3` sin seed/migration workflow claro.

### G. Reproducibilidad de Entorno

Evidencia: `.venv/Scripts/python.exe -m pip freeze`.

```text
WARNING: Ignoring invalid distribution ~ip (C:\Users\cbola�o\Downloads\poryecto conexiones\.venv\Lib\site-packages)
asgiref==3.12.1
Django==6.1.1
sqlparse==0.6.0
tzdata==2026.4
```

Evidencia de Python usado:

```text
C:\Users\cbola�o\Downloads\poryecto conexiones\.venv\Scripts\python.exe
3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]
```

Lectura:
- No hay `requirements.txt`, `pyproject.toml`, `setup.cfg` ni `Pipfile`.
- El entorno es reproducible solo por convencion local, no por archivo versionado.
- Hay una advertencia de pip sobre una distribucion invalida `~ip`, probablemente metadata corrupta de pip en `.venv`; no bloquea el freeze, pero conviene limpiar o recrear el entorno luego.

### H. Brecha de Branch / Release Strategy

Evidencia Git:

```text
* master c82bdb1 [origin/master] creating the proyect
remotes/origin/master c82bdb1 creating the proyect
origin/master c82bdb1
```

Hechos:
- Solo existe `master`.
- No hay evidencia local de ramas feature, tags, PRs, protecciones o CI.
- No se puede verificar proteccion de ramas desde este entorno local sin consultar configuracion de GitHub con permisos adecuados.

Brecha proporcional para proyecto temprano:
- Falta una regla minima de ramas: `master` estable y trabajo en ramas cortas por feature/fix.
- Falta convencion de PR chica y revisable, alineada con el presupuesto de 800 lineas cambiadas.
- Falta politica simple para migraciones: una persona integra primero o se re-generan migraciones tras rebase para evitar `0002` duplicadas.
- Falta CI minimo para `python manage.py test --noinput` y `makemigrations --check --dry-run`.

## Opciones Consideradas

### 1. Manejo del `SECRET_KEY` ya empujado

Opcion A: rotar el valor y moverlo a variable de entorno sin reescribir historia.
- Pros: bajo riesgo, apropiado para repo temprano, evita romper clones existentes.
- Contras: el secreto viejo sigue reachable en historia publica/remota.
- Complejidad: baja.

Opcion B: rotar el valor, moverlo a variable de entorno y reescribir historia.
- Pros: elimina el secreto del historial visible si todos coordinan y el remoto acepta force push.
- Contras: rompe clones, requiere coordinacion, no garantiza que nadie haya copiado el secreto antes.
- Complejidad: media/alta para un equipo estudiante.

Opcion C: no hacer nada por ahora.
- Pros: cero trabajo inmediato.
- Contras: mantiene una mala practica de seguridad y normaliza secretos hardcodeados.
- Complejidad: baja, pero mala direccion tecnica.

### 2. Manejo de `db.sqlite3` trackeado

Opcion A: dejar de trackear `db.sqlite3`, agregarlo a `.gitignore`, crear migraciones/seed para reconstruir datos demo.
- Pros: flujo sano para equipo, evita compartir datos/sesiones, reduce conflictos binarios.
- Contras: cada dev debe migrar y seedear localmente.
- Complejidad: baja/media.

Opcion B: mantener `db.sqlite3` como fixture compartida temporal.
- Pros: onboarding rapido.
- Contras: binario conflictivo, mezcla datos/sesiones, no escala con migraciones.
- Complejidad: baja ahora, costosa despues.

Opcion C: reemplazar la DB por fixtures JSON o comando seed versionado.
- Pros: reproducible y revisable; encaja con `seed_demo.py` existente.
- Contras: requiere mantener fixture/seed al cambiar modelos.
- Complejidad: media.

### 3. Split de settings por entorno

Opcion A: un solo `settings.py` con `os.environ` para `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` y DB.
- Pros: cambio pequeno, facil de entender, suficiente para etapa temprana.
- Contras: puede crecer desordenado si el proyecto madura.
- Complejidad: baja.

Opcion B: paquete `settings/` con `base.py`, `local.py`, `production.py`.
- Pros: separacion clara de ambientes.
- Contras: mas archivos y friccion para un equipo nuevo.
- Complejidad: media.

Opcion C: incorporar `django-environ` o similar.
- Pros: ergonomia para `.env`.
- Contras: dependencia adicional y convencion nueva; todavia no hay manifest de dependencias.
- Complejidad: baja/media.

## Direccion Recomendada

Exploracion no decide, pero la direccion mas proporcional es:
- Crear higiene base primero: `.gitignore`, manifest de dependencias, variables de entorno minimas, y dejar de trackear `.pyc`/`db.sqlite3` en una fase posterior.
- Rotar `SECRET_KEY` y moverlo a entorno; no reescribir historia salvo que el usuario confirme que nadie mas depende del repo y acepta el costo.
- Mantener un `settings.py` unico con env vars por ahora; split por entorno solo cuando haya despliegue real o configuraciones divergentes.
- Crear las migraciones pendientes antes de que varios desarrolladores trabajen en paralelo, porque el conflicto de `0002` es casi seguro.
- Usar ramas cortas + PRs chicas, con CI minimo de tests y `makemigrations --check --dry-run`.

Razonamiento: el repo esta temprano, pero ya tiene modelos cruzados y una DB con datos/sesiones. La prioridad no es ceremonia enterprise; es evitar que el equipo construya sobre un piso inestable.

## Preguntas Abiertas para Decision del Usuario

- El `SECRET_KEY` ya empujado: rotar sin reescribir historia, o coordinar limpieza de historia con force push?
- `db.sqlite3`: se considera descartable/demo y debe salir de Git, o hay algun dato que el equipo necesita preservar/exportar?
- Settings: preferis mantener un `settings.py` con env vars por simplicidad, o separar `base/local/production` desde ahora?
- Branching: el equipo acepta trabajar con ramas feature + PR, o por ahora quiere commits directos a `master` con reglas minimas?
- Migraciones pendientes: se generan todas juntas como baseline de sincronizacion, o se quieren revisar por dominio antes?

## Riesgos

- El secreto ya esta en `origin/master`; aunque se rote, no se puede probar desde Git local si alguien lo clono.
- `db.sqlite3` contiene usuarios, sesiones y datos de dominio; podria tener datos no-demo sin inspeccionar filas.
- Los modelos actuales no coinciden con migraciones; si varios devs generan migraciones al mismo tiempo, chocaran.
- El repositorio no tiene CI ni tests reales; cualquier limpieza puede parecer segura localmente pero romper comportamiento no cubierto.
- Sin manifest de dependencias, otro desarrollador puede instalar versiones distintas aunque hoy el `.venv` tenga Django 6.1.1.
