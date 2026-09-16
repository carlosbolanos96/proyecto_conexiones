# Proposal: Repo Git Higiene

## Intent

Sanear el repositorio antes de sumar mas desarrollo: sacar artefactos locales de Git, mover secretos a entorno, sincronizar migraciones y dejar un flujo minimo para colaborar sin pisarse. El proyecto es temprano y estudiantil, asi que la propuesta evita ceremonia enterprise.

## Scope

### In Scope
- Agregar `.gitignore` para bytecode Python, `.venv/`, artefactos Django, IDEs, `.env`, archivos OS y SQLite local.
- Remover de tracking los 92 `.pyc` y `db.sqlite3`, manteniendolos en disco local.
- Crear manifest de dependencias con pins verificados: `asgiref==3.12.1`, `Django==6.1.1`, `sqlparse==0.6.0`, `tzdata==2026.4`.
- Refactorizar `conexiones/settings.py`: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` y configuracion sensible por variables de entorno; commitear `.env.example`.
- Generar/resolver migraciones `0002` para las 11 apps fuera de sync.
- Documentar workflow multi-dev simple: ramas cortas, PRs chicos, conventional commits basicos y regla para migraciones.
- Agregar README/CONTRIBUTING con setup local, migraciones, seed demo y test command.
- Agregar tests reales minimos: smoke test de boot del proyecto y carga de apps.

### Out of Scope
- Reescribir logica de negocio.
- Construir la capa HTTP vacia de las 11 apps no cableadas.
- Microservicios, Docker, Kubernetes o infraestructura no necesaria para un equipo chico.
- Ceremonia enterprise: CODEOWNERS obligatorio, release trains o semantic versioning formal mas alla de conventional commits basicos.

## Capabilities

### New Capabilities
- `repo-hygiene`: reglas de tracking, secretos, dependencias, setup local y colaboracion Git.

### Modified Capabilities
- None

## Approach

Hacer primero la higiene base en cambios revisables: `.gitignore` + untracking, settings por entorno, manifest, migraciones, tests smoke y documentacion. No tocar funcionalidades ni URLs de dominio. Evitar limpieza destructiva de historial hasta que el usuario confirme las decisiones abiertas.

## Open Decisions

| Decision | Options / Tradeoffs | Recommendation | Blocking |
|---|---|---|---|
| `SECRET_KEY` ya esta en `origin/master` | A) Rotar, mantener historia: simple; el valor viejo queda comprometido pero solo protege sesiones y no hay usuarios reales confirmados. B) Rotar + reescribir historia: limpia el repo visible, rompe clones y exige force push. C) Rotar + borrar/recrear remoto: mas limpio, pero pierde continuidad del URL/historia GitHub. | A, por proporcionalidad para proyecto estudiantil temprano. Si luego se confirma exposicion sensible real, evaluar B/C. | No para tasks de higiene; si bloquea cualquier purge de historia. |
| Usuario no-demo en `db.sqlite3` | A) Untrack DB y decidir offline que hacer con esa cuenta; purgar historia solo si confirman dato real. B) Untrack + purgar historia ahora: reduce exposicion, pero seria actuar sin confirmar. | A. No inspeccionar contenido ni reproducir datos; pedir confirmacion humana antes de purgar. | Si para history purge; no para untracking. |
| Estructura de settings | A) Unico `settings.py` con env vars y defaults sanos: menos colision y facil. B) `settings/base.py`, `local.py`, `production.py`: mas orden futuro, mas archivos. C) `django-environ`/`python-decouple`: ergonomico, agrega dependencia. | A. Soluciona el secreto con minima complejidad. | No. |
| Migraciones `0002` faltantes | A) Generar las 11 juntas ahora: commit grande pero evita choques antes de que otros branchen. B) Por app/dominio: revisable, pero mas friccion. C) Regenerar `0001` borrando migraciones: limpio, pero destructivo para quien ya aplico `0001`. | A, antes de mas ramas. | No, pero debe resolverse antes de trabajo paralelo. |
| Branching model | A) Trunk-based con ramas cortas + PR: simple y con review. B) Git-flow: demasiado pesado. C) Push directo a `master`: rapido, sin red de seguridad. | A, con PRs chicos bajo presupuesto de 800 lineas. | No para documentar; si para imponer protecciones remotas. |

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `.gitignore`, `requirements.txt`, `.env.example` | New | Reproducibilidad e higiene local. |
| `conexiones/settings.py` | Modified | Configuracion por entorno sin secreto hardcodeado. |
| `*/migrations/` | Modified | Agregar `0002` para 11 apps. |
| `db.sqlite3`, `*.pyc` | Removed from tracking | Mantener en disco, sacar del repositorio. |
| `README.md`, `CONTRIBUTING.md`, tests | New/Modified | Setup, workflow y verificacion minima. |

## Risks

| Risk | Likelihood | Mitigation |
|---|---:|---|
| Untrackear `db.sqlite3` no lo elimina del historial Git. | High | Explicitarlo y no purgar sin confirmacion del usuario. |
| Las 11 migraciones juntas se vuelven hotspot si otros branchan antes. | High | Integrarlas primero, antes de trabajo paralelo. |
| Rotar `SECRET_KEY` invalida sesiones locales. | Med | Aceptable; son sesiones dev/demo. Documentar regeneracion de `.env`. |
| Sacar la DB puede revelar falta de seed/migrations correctas. | Med | Test smoke + setup documentado + `migrate`/seed. |

## Rollback Plan

Revertir `.gitignore`, manifest, `.env.example`, README/CONTRIBUTING y tests es seguro con un revert normal. Cambios en `settings.py` son revertibles si se conserva un `.env.example` claro. Migraciones nuevas deben revertirse con cuidado si ya fueron aplicadas por alguien. History rewrite, borrado/recreacion del remoto y purga de DB no son rollback seguro. Untrackear `db.sqlite3` no borra el archivo local, pero puede perder datos si alguien elimina su copia sin backup.

## Dependencies

- Decision humana sobre historial del `SECRET_KEY` y posible dato real en `db.sqlite3` antes de cualquier purge.
- Python/Django local existente y dependencias verificadas por freeze.
- Specs/diseño SDD antes de implementar.

## Success Criteria

- [ ] `git status` no muestra `.pyc` ni `db.sqlite3` como trackeados.
- [ ] Un dev nuevo puede crear entorno, instalar deps, migrar, seedear y correr el proyecto desde README.
- [ ] `SECRET_KEY` no queda hardcodeado en `settings.py`; `.env.example` documenta variables.
- [ ] `makemigrations --check --dry-run` pasa.
- [ ] `python manage.py test --noinput` corre al menos smoke tests reales.
- [ ] El workflow Git documenta ramas cortas, PRs chicos y manejo de migraciones.
