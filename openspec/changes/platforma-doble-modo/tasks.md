# Tasks: Plataforma Doble Modo

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~1,120 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR1 shared foundation -> PR2 restaurant/agro catalogs -> PR3 orders/payments/delivery/inventory |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | App scaffolding, settings, locations, accounts | PR 1 | Base domain dependencies. |
| 2 | Agro, restaurants, menus | PR 2 | Catalog models and admin. |
| 3 | Orders, payments, notifications, delivery, warehouses, inventory | PR 3 | Cross-app commerce and stock. |

## Checklist

- [x] **T1: Scaffold apps** — Run `startapp` for `accounts`, `locations`, `orders`, `payments`, `notifications`, `restaurants`, `menus`, `delivery`, `agro`, `warehouses`, `inventory`. Acceptance: each app has standard Django files. Estimate: ~220 lines.
- [x] **T2: Register apps and confirm URLs** — Touch `conexiones/settings.py` and `conexiones/urls.py`; add all domain apps after `core`, keep `/` and `/admin/` only. Acceptance: no `AUTH_USER_MODEL`; no placeholder app URL includes. Estimate: ~15 lines.
- [x] **T3: Locations model/admin** — Touch `locations/models.py`, `locations/admin.py`; add `Address` with owner fields, coordinates, default constraint, indexes, ordering. Acceptance: `Address` registered in admin. Estimate: ~55 lines.
- [x] **T4: Accounts model/admin** — Touch `accounts/models.py`, `accounts/admin.py`; add `Profile` with roles, phone, avatar, default address validation. Acceptance: role index and admin registration exist. Estimate: ~65 lines.
- [x] **T5: Agro model/admin** — Touch `agro/models.py`, `agro/admin.py`; add `Producer` and `Product` with role validation, unit choices, price validators, constraints. Acceptance: both models registered. Estimate: ~95 lines.
- [x] **T6: Restaurants model/admin** — Touch `restaurants/models.py`, `restaurants/admin.py`; add `Restaurant` with owner, address, active flag, owner/name constraint. Acceptance: admin registration exists. Estimate: ~45 lines.
- [x] **T7: Menus model/admin** — Touch `menus/models.py`, `menus/admin.py`; add `RestaurantProduct` with restaurant FK, price validator, availability, constraint. Acceptance: admin registration exists. Estimate: ~50 lines.
- [x] **T8: Orders model/admin** — Touch `orders/models.py`, `orders/admin.py`; add `Order` and `OrderItem` with mode/status choices, address-owner validation, exactly-one product constraint, mode/product validation. Acceptance: both models registered. Estimate: ~125 lines.
- [x] **T9: Payments model/admin** — Touch `payments/models.py`, `payments/admin.py`; add one-to-one `Payment`, method/status choices, amount validator. Acceptance: admin registration exists. Estimate: ~45 lines.
- [x] **T10: Notifications model/admin** — Touch `notifications/models.py`, `notifications/admin.py`; add `Notification` with type choices, unread default, timestamps, indexes. Acceptance: admin registration exists. Estimate: ~40 lines.
- [x] **T11: Delivery model/admin** — Touch `delivery/models.py`, `delivery/admin.py`; add `Courier` and `Delivery` with role/order-mode validation and status lifecycle fields. Acceptance: both models registered. Estimate: ~90 lines.
- [x] **T12: Warehouses model/admin** — Touch `warehouses/models.py`, `warehouses/admin.py`; add `Warehouse` with producer, address, active flag, producer/name constraint. Acceptance: admin registration exists. Estimate: ~45 lines.
- [x] **T13: Inventory model/admin** — Touch `inventory/models.py`, `inventory/admin.py`; add `InventoryItem` with stock validator, warehouse/product uniqueness, same-producer validation. Acceptance: admin registration exists. Estimate: ~55 lines.
- [x] **T14: Initial migrations** — Run `python manage.py makemigrations accounts locations orders payments notifications restaurants menus delivery agro warehouses inventory`. Acceptance: each app has `migrations/0001_initial.py`; dependencies are valid. Estimate: ~175 lines.
- [x] **T15: Final verification** — Run `python manage.py check` and `python manage.py makemigrations --check`. Acceptance: both commands exit 0. Estimate: 0 lines.
