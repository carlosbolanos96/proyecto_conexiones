# Verification Report: Plataforma Doble Modo

**Change**: `platforma-doble-modo`
**Version**: N/A
**Mode**: Standard SDD verify
**Summary verdict**: FAIL

The implementation passes Django system checks and migration drift checks, and static source inspection found matching model/admin implementations for all 19 requirements. However, `manage.py test` discovered and ran 0 tests, so no spec scenario has runtime coverage. Under the SDD verify gate, scenario compliance cannot be marked PASS without passing covering tests.

## Completeness

| Metric | Value |
|---|---:|
| Tasks total | 15 |
| Tasks complete | 15 |
| Tasks incomplete | 0 |
| Requirements inspected | 19 |
| Requirements statically implemented | 19 |
| Requirements missing | 0 |
| Spec scenarios | 26 |
| Scenarios covered by passing tests | 0 |
| Scenarios untested | 26 |

`apply-progress.md` was requested if present, but it does not exist at `openspec/changes/platforma-doble-modo/apply-progress.md`.

## Commands Run

### Django System Check

Command:

```text
.venv/Scripts/python.exe manage.py check
```

Output:

```text
System check identified no issues (0 silenced).
```

Result: OK.

### Migration Drift Check

Command:

```text
.venv/Scripts/python.exe manage.py makemigrations --check --dry-run
```

Output:

```text
No changes detected
```

Result: OK.

### Test Suite

Command:

```text
.venv/Scripts/python.exe manage.py test
```

Output:

```text
Found 0 test(s).
System check identified no issues (0 silenced).
----------------------------------------------------------------------
Ran 0 tests in 0.000s

NO TESTS RAN
```

Result: CRITICAL. No runtime tests cover the spec scenarios.

### Admin Registry Smoke Check

Command:

```text
.venv/Scripts/python.exe manage.py shell -c "from django.contrib import admin; from accounts.models import Profile; from locations.models import Address; from orders.models import Order, OrderItem; from payments.models import Payment; from notifications.models import Notification; from restaurants.models import Restaurant; from menus.models import RestaurantProduct; from delivery.models import Courier, Delivery; from agro.models import Producer, Product; from warehouses.models import Warehouse; from inventory.models import InventoryItem; models=[Profile,Address,Order,OrderItem,Payment,Notification,Restaurant,RestaurantProduct,Courier,Delivery,Producer,Product,Warehouse,InventoryItem]; missing=[m.__name__ for m in models if m not in admin.site._registry]; print('admin_registry_missing=', missing); print('admin_registry_count=', len(models)-len(missing), '/', len(models))"
```

Output:

```text
26 objects imported automatically (use -v 2 for details).

admin_registry_missing= []
admin_registry_count= 14 / 14
```

Result: OK.

## Per-Requirement Checklist

| Requirement | Status | Evidence |
|---|---|---|
| ACCT-1 | OK, UNTESTED | `accounts/models.py:6-37` defines `Profile`; `user` is `OneToOneField`; `role` uses `TextChoices` with `consumer`, `producer`, `courier`, `warehouse_manager`; `phone` and `avatar` are blankable; `default_address` is nullable and validated in `clean()` against the same user. |
| ACCT-2 | OK, UNTESTED | `accounts/admin.py:6-11` registers `ProfileAdmin` with role, phone, avatar/default address management through admin fields. |
| COMM-1 | OK, UNTESTED | `locations/models.py:5-33` defines `Address` with required owner/street/number/city/province, optional postal code and coordinates, `is_default`, owner/city indexes, and conditional unique constraint `one_default_address_per_user`. |
| COMM-2 | OK, UNTESTED | `orders/models.py:9-47` defines `Order` with consumer, mode choices, status choices/default, delivery address, non-negative total, timestamps, and address-owner validation; `orders/models.py:49-99` defines `OrderItem` with positive quantity/unit price, exact-one-product DB constraint, and mode/product validation. |
| COMM-3 | OK, UNTESTED | `payments/models.py:7-33` defines one-to-one `Payment` with method choices, status choices/default, positive amount validator, created timestamp, and status index. |
| COMM-4 | OK, UNTESTED | `notifications/models.py:5-29` defines `Notification` with user FK, type choices, required message, `is_read=False`, timestamp, indexes, and ordering. |
| COMM-5 | OK, UNTESTED | `locations/admin.py`, `orders/admin.py`, `payments/admin.py`, and `notifications/admin.py` register `Address`, `Order`, `OrderItem`, `Payment`, and `Notification`; shell smoke confirmed all expected MVP models are in `admin.site._registry`. |
| REST-1 | OK, UNTESTED | `restaurants/models.py:5-20` defines `Restaurant`; `menus/models.py:7-25` defines `RestaurantProduct` with required restaurant/name and positive price validator. |
| REST-2 | OK, UNTESTED | `delivery/models.py:5-30` defines `Courier`; `profile` is one-to-one, `vehicle_type` uses choices, `is_available` defaults false, blank fields are allowed, and `clean()` enforces courier role. |
| REST-3 | OK, UNTESTED | `delivery/models.py:33-58` defines one-to-one `Delivery`, nullable courier, lifecycle status choices/default, nullable timestamps, status index, and `clean()` restricts delivery to restaurant orders. |
| REST-4 | OK, UNTESTED | `restaurants/admin.py`, `menus/admin.py`, and `delivery/admin.py` register `Restaurant`, `RestaurantProduct`, `Courier`, and `Delivery`; shell smoke confirmed registration. |
| AGRO-1 | OK, UNTESTED | `agro/models.py:8-27` defines `Producer`; `profile` is one-to-one, business name/tax/address are required, description is blankable, `tax_id` is unique, and `clean()` enforces producer role. |
| AGRO-2 | OK, UNTESTED | `agro/models.py:30-54` defines `Product`; producer/name/price/unit are required, price uses `MinValueValidator(Decimal('0.01'))`, unit choices are `kg`, `box`, `unit`, and producer/name uniqueness exists. |
| AGRO-3 | OK, UNTESTED | `warehouses/models.py:4-18` defines `Warehouse`; `inventory/models.py:8-30` defines `InventoryItem` with non-negative quantity validator, warehouse/product uniqueness, and `clean()` enforcing same producer. |
| AGRO-4 | OK, UNTESTED | `agro/admin.py`, `warehouses/admin.py`, and `inventory/admin.py` register `Producer`, `Product`, `Warehouse`, and `InventoryItem`; shell smoke confirmed registration. |
| STRU-1 | OK, UNTESTED | `conexiones/settings.py:33-52` registers `core`, shared apps, restaurant mode apps, agro mode apps, and Django contrib apps. No `AUTH_USER_MODEL` override was found in settings. |
| STRU-2 | OK, UNTESTED | Shared order/payment/notification/address concerns are in `orders`, `payments`, `notifications`, `locations`; restaurant catalog is in `restaurants`/`menus`; agro products, warehouses, and inventory are in `agro`/`warehouses`/`inventory`. |
| STRU-3 | OK, UNTESTED | `conexiones/urls.py:20-23` keeps only home via `core.urls` and admin; `core/models.py:1-3` contains no domain models. This matches the design direction to avoid placeholder app URL includes until public views exist. |
| STRU-4 | OK, UNTESTED | All 14 MVP domain models were imported and confirmed registered in `admin.site._registry`: `Profile`, `Address`, `Order`, `OrderItem`, `Payment`, `Notification`, `Restaurant`, `RestaurantProduct`, `Courier`, `Delivery`, `Producer`, `Product`, `Warehouse`, `InventoryItem`. |

## Spec Compliance Matrix

| Requirement | Scenario Count | Runtime Test Evidence | Result |
|---|---:|---|---|
| ACCT-1 | 2 | None found; `manage.py test` ran 0 tests. | UNTESTED |
| ACCT-2 | 1 | None found; `manage.py test` ran 0 tests. | UNTESTED |
| COMM-1 | 2 | None found; `manage.py test` ran 0 tests. | UNTESTED |
| COMM-2 | 2 | None found; `manage.py test` ran 0 tests. | UNTESTED |
| COMM-3 | 1 | None found; `manage.py test` ran 0 tests. | UNTESTED |
| COMM-4 | 1 | None found; `manage.py test` ran 0 tests. | UNTESTED |
| COMM-5 | 1 | Admin registry shell smoke passed, but no Django test covers the scenario. | UNTESTED |
| REST-1 | 2 | None found; `manage.py test` ran 0 tests. | UNTESTED |
| REST-2 | 2 | None found; `manage.py test` ran 0 tests. | UNTESTED |
| REST-3 | 1 | None found; `manage.py test` ran 0 tests. | UNTESTED |
| REST-4 | 1 | Admin registry shell smoke passed, but no Django test covers the scenario. | UNTESTED |
| AGRO-1 | 2 | None found; `manage.py test` ran 0 tests. | UNTESTED |
| AGRO-2 | 1 | None found; `manage.py test` ran 0 tests. | UNTESTED |
| AGRO-3 | 2 | None found; `manage.py test` ran 0 tests. | UNTESTED |
| AGRO-4 | 1 | Admin registry shell smoke passed, but no Django test covers the scenario. | UNTESTED |
| STRU-1 | 1 | `manage.py check` passed; no dedicated test. | UNTESTED |
| STRU-2 | 1 | Static source inspection only. | UNTESTED |
| STRU-3 | 1 | Static source inspection only. | UNTESTED |
| STRU-4 | 1 | Admin registry shell smoke passed, but no Django test covers the scenario. | UNTESTED |

**Compliance summary**: 0/26 scenarios compliant by SDD runtime-test standard; 26/26 scenarios have static implementation evidence.

## Validations Confirmed

| Validation Area | Confirmed Evidence |
|---|---|
| Role choices | `accounts.Profile.Role` includes `consumer`, `producer`, `courier`, `warehouse_manager`. |
| Order mode choices | `orders.Order.Mode` includes `restaurant`, `agro`. |
| Order status choices | `orders.Order.Status` includes `pending`, `confirmed`, `in_delivery`, `delivered`, `cancelled`. |
| Delivery status choices | `delivery.Delivery.Status` includes `pending`, `picked_up`, `in_transit`, `delivered`. |
| Payment method choices | `payments.Payment.Method` includes `cash`, `card`, `transfer`, `simulated`. |
| Payment status choices | `payments.Payment.Status` includes `pending`, `approved`, `rejected`, `refunded`. |
| Notification type choices | `notifications.Notification.Type` includes `order`, `payment`, `delivery`, `system`. |
| Vehicle type choices | `delivery.Courier.Vehicle` includes `bike`, `motorcycle`, `car`, `van`. |
| Agro unit choices | `agro.Product.Unit` includes `kg`, `box`, `unit`. |
| Price > 0 | `agro.Product.price`, `menus.RestaurantProduct.price`, `orders.OrderItem.unit_price`, `payments.Payment.amount` use `MinValueValidator(Decimal('0.01'))`. |
| Quantity > 0 | `orders.OrderItem.quantity` uses `MinValueValidator(Decimal('0.01'))`. |
| Stock quantity >= 0 | `inventory.InventoryItem.quantity` uses `MinValueValidator(Decimal('0.00'))`. |
| Order total >= 0 | `orders.Order.total` uses `MinValueValidator(Decimal('0.00'))`. |
| Default address owner | `accounts.Profile.clean()` validates the default address belongs to the same user. |
| Order delivery address owner | `orders.Order.clean()` validates delivery address owner matches consumer. |
| Exactly one order item product | `orders.OrderItem` has DB `CheckConstraint` and `clean()` validation. |
| Order item product matches mode | `orders.OrderItem.clean()` validates restaurant/agro product FK by order mode. |
| Producer role | `agro.Producer.clean()` validates profile role is `producer`. |
| Courier role | `delivery.Courier.clean()` validates profile role is `courier`. |
| Restaurant-only delivery | `delivery.Delivery.clean()` validates order mode is `restaurant`. |
| Inventory same producer | `inventory.InventoryItem.clean()` validates warehouse producer equals product producer. |
| Required FKs | Required FKs are non-null by default where specs require them; optional FKs explicitly use `null=True, blank=True`. |
| Uniqueness | One-to-one fields and unique constraints implement unique profile/payment/delivery relationships and per-owner/per-producer uniqueness rules. |

## Design Coherence

| Design Decision | Followed? | Evidence |
|---|---|---|
| Modular Django monolith | Yes | 11 domain apps are registered in `conexiones/settings.py`; no microservice split. |
| Keep Django default `auth.User` plus `Profile` | Yes | Models use `settings.AUTH_USER_MODEL`; no `AUTH_USER_MODEL` override in settings. |
| Separate restaurant and agro products | Yes | `menus.RestaurantProduct` and `agro.Product` are separate models. |
| Shared order with `mode` choices | Yes | `orders.Order` has `mode` choices for `restaurant` and `agro`. |
| Explicit order item FKs | Yes | `orders.OrderItem` has explicit nullable FKs to `RestaurantProduct` and `agro.Product` plus exact-one constraint. |
| Cross-app validation in `clean()` | Yes | Role, address-owner, product-mode, delivery-mode, and inventory-producer validations live in model `clean()` methods. |
| Admin registration for MVP models | Yes | Shell smoke confirmed 14/14 expected models registered. |
| `Profile.avatar` as `ImageField` in final design | Partial | Implementation uses `URLField(blank=True)` instead of `ImageField(upload_to='profiles/', blank=True)`. The spec only requires avatar may be blank, but this deviates from the design model definition. |

## Issues Found

### CRITICAL

- No runtime tests exist for the 26 spec scenarios. `manage.py test` found 0 tests, so the SDD verify gate cannot mark any scenario as compliant even though static implementation evidence is strong.

### WARNING

- `accounts.Profile.avatar` is implemented as `URLField(blank=True)`, while the design's final model definition says `ImageField(upload_to='profiles/', blank=True)`. This does not violate the account spec text, which only says avatar may be blank, but it is a design deviation.
- No end-to-end schema smoke test was committed or retained. I ran an admin registry shell smoke only, avoiding database pollution.

### SUGGESTION

- Add focused Django `TestCase` coverage for model validation scenarios before archive: role validation, invalid choices, price/quantity validators, address-owner validation, exactly-one order item product, mode/product validation, delivery mode validation, inventory same-producer validation, and admin registration.

## Verdict

FAIL.

The code passes Django checks and static inspection against all 19 requirements, but the SDD verification gate requires passing runtime coverage for scenarios. With 0 tests run, the change should be fixed with focused tests and reverified before `sdd-archive`.
