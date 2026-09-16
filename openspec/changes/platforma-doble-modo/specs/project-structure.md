# Project Structure Specification

## Purpose

Define the Django app layout and routing responsibilities for the dual-mode modular monolith.

## Requirements

### Requirement: STRU-1 Modular app registration

The system MUST organize domain code into shared apps, restaurant mode apps, agro mode apps, and the existing `core` app.

Validation: Django app names MUST be unique; shared apps MUST be `accounts`, `locations`, `orders`, `payments`, `notifications`; restaurant mode apps MUST be `restaurants`, `menus`, `delivery`; agro mode apps MUST be `agro`, `warehouses`, `inventory`.

#### Scenario: Register domain apps

- GIVEN the project settings are loaded
- WHEN Django starts
- THEN all domain apps are available for models, admin, and migrations

### Requirement: STRU-2 Responsibility boundaries

The system MUST keep shared commerce concerns out of mode-specific apps and MUST keep mode-specific catalog or inventory concerns out of shared apps.

#### Scenario: Shared order reused by modes

- GIVEN restaurant and agro modes both create purchases
- WHEN an order is stored
- THEN common order data lives in `orders`
- AND mode-specific product data remains in its mode app

### Requirement: STRU-3 URL and template organization

The system SHOULD keep `core` responsible for home/navigation and SHOULD expose app URLs by domain or mode when public pages are added.

Validation: URL namespaces SHOULD be unique; shared templates SHOULD live under the owning app or project template directory; `core` SHOULD NOT own domain models.

#### Scenario: Add mode landing page

- GIVEN a public restaurant or agro page is added
- WHEN routing is configured
- THEN the route is namespaced to its owning app
- AND home navigation can link to it from `core`

### Requirement: STRU-4 Admin availability across apps

The system MUST provide Django admin access for every MVP domain model defined by the account, commerce, restaurant, and agro specs.

#### Scenario: Staff sees all MVP models

- GIVEN staff is logged in to `/admin`
- WHEN they review registered models
- THEN every MVP model appears under its owning app

## Files/Key Objects

- `conexiones/settings.py`: registers current and future domain apps.
- `conexiones/urls.py`: includes app URLs when public routes exist.
- `core/`: home, navigation, and public entry pages only.
- Each domain app: `apps.py`, `models.py`, `admin.py`, optional `urls.py`, views, and templates owned by that domain.
