# conexiones

Plataforma que conecta productores y consumidores con dos modos: **restaurantes/delivery** y **agro/bodegas**.

Django 6.1 · Python 3.14 · SQLite

---

## Setup desde cero

Clonás el repo y con cuatro comandos tenés todo andando:

```bash
git clone https://github.com/carlosbolanos96/proyecto_conexiones.git
cd conexiones

python -m venv .venv
.venv/Scripts/pip install -r requirements.txt    # Linux/Mac: .venv/bin/pip

.venv/Scripts/python manage.py migrate
.venv/Scripts/python manage.py seed_demo --create-admin
.venv/Scripts/python manage.py runserver
```

`seed_demo` crea la base de ejemplo completa: 12 usuarios de prueba, restaurantes, productores, bodegas, productos, órdenes, pagos y deliveries. **No tenés que crear datos a mano nunca.**

Es **idempotente**: podés correrlo las veces que quieras, borra lo `demo_*` y lo recrea. Si arruinás algo mientras experimentally, volvés a correrlo y volvés a cero.

### Accesos

| Qué | Dónde | Credenciales |
|-----|-------|--------------|
| Admin | http://localhost:8000/admin/ | `admin` / `admin12345` |
| Home | http://localhost:8000/ | — |

> Las credenciales son de demo y están en el código a propósito. **No las uses en producción.**

### Usuarios de prueba

Todos con password `demo12345`:

| Prefijo | Rol | Cantidad |
|---------|-----|----------|
| `demo_consumer_*` | Comprador | 3 |
| `demo_producer_*` | Productor agro | 3 |
| `demo_courier_*` | Repartidor | 3 |
| `demo_manager_*` | Encargado de local | 3 |

---

## Flujo de trabajo en Git

Este repo sigue **trunk-based**: `master` es siempre desplegable y nadie commitea directo.

```bash
git checkout master
git pull                          # siempre actualizás antes de empezar

git checkout -b mi-feature        # branch corta con tu nombre + qué hacés
# ... trabajás ...
git add .
git commit -m "feat: descripcion corta"
git push -u origin mi-feature

# Abrís PR contra master, pide review, mergeas, borrás la branch
```

Reglas:

- **Branch por feature**, no por persona. Se borra al mergear.
- **PR siempre contra `master`.** Nadie pushea directo a `master`.
- **`git add .` es seguro**: el `.gitignore` filtra bytecode, base de datos, `.venv` y `.env`.
- Commits convencionales: `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`.

### La base de datos NO se versiona

`db.sqlite3` está en `.gitignore` a propósito. Cada dev genera la suya con `migrate` + `seed_demo`.

Si commiteás la base, cada merge es un conflicto binario que Git no puede resolver, y el schema de cada uno empieza a divergir.

---

## Estructura

| App | Responsabilidad |
|-----|-----------------|
| `core/` | Home, navegación, comando `seed_demo` |
| `conexiones/` | Configuración del proyecto (settings, urls, wsgi) |
| **Compartidas** | |
| `accounts/` | Usuarios, perfiles y roles |
| `locations/` | Direcciones y zonas |
| `orders/` | Órdenes y estados |
| `payments/` | Pagos (simulados por ahora) |
| `notifications/` | Notificaciones |
| **Modo restaurantes** | |
| `restaurants/` | Restaurantes |
| `menus/` | Catálogo y productos |
| `delivery/` | Despacho y repartidores |
| **Modo agro** | |
| `agro/` | Productores y productos |
| `warehouses/` | Bodegas |
| `inventory/` | Stock |

---

## Tests

```bash
python manage.py test               # 13 tests, ~20s
python manage.py test orders        # una sola app
python manage.py test -v 2          # ver nombres de cada test
```

Cubren las 9 reglas de negocio que viven en los `clean()` de los modelos.

### La trampa de `full_clean()`

Las reglas de negocio están en `Model.clean()`. **Django NO las ejecuta solo.**

```python
# Esto GUARDA un registro inválido, sin error:
courier = Courier.objects.create(profile=perfil_de_un_consumidor)

# Esto lo RECHAZA:
courier.full_clean()
```

`Model.objects.create()` y `Model.save()` no llaman `full_clean()`. Si creás datos desde una vista, un formulario o un comando, **llamá `full_clean()` vos** antes de guardar. Hay un test que documenta exactamente esto: `accounts.tests.ProfileValidationTests.test_objects_create_does_not_run_model_clean`.

`seed_demo` sí lo hace bien: su helper `_save()` llama `full_clean()` antes de cada `save()`.

## Comandos útiles

```bash
python manage.py makemigrations      # después de cambiar models.py
python manage.py migrate            # aplicar migraciones
python manage.py seed_demo --create-admin   # resetear datos de ejemplo
python manage.py test               # correr tests
python manage.py shell              # consola interactiva
```

## Migraciones

Los modelos y las migraciones tienen que estar sincronizados. Antes de crear un PR:

```bash
python manage.py makemigrations --check --dry-run
```

Si sale con cambios pendientes, corré `makemigrations` y commiteá el archivo generado **junto con** el cambio de modelo.
