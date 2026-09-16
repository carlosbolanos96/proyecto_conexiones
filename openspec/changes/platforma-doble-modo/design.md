# Design: Plataforma Doble Modo

## Technical Approach

Build a modular Django monolith around the existing `core` app. `core` keeps the public home page; new domain apps own models, admin, and later their own URLs/templates. Use Django's default `auth.User`; `accounts.Profile` extends it with one role. Shared commerce stays in `locations`, `orders`, `payments`, and `notifications`; restaurant and agro catalog data stays mode-specific.

## App Creation Order

Run exactly:

```bash
python manage.py startapp accounts
python manage.py startapp locations
python manage.py startapp orders
python manage.py startapp payments
python manage.py startapp notifications
python manage.py startapp restaurants
python manage.py startapp menus
python manage.py startapp delivery
python manage.py startapp agro
python manage.py startapp warehouses
python manage.py startapp inventory
```

This order follows dependency direction: identity first, addresses before profiles/vendors/orders, orders before payments/delivery, then mode catalogs, then warehouse stock.

## Architecture Decisions

| Decision | Choice | Alternatives | Rationale |
|---|---|---|---|
| User model | Keep Django `User` plus `Profile` OneToOne | Custom user | MVP avoids auth migration risk. |
| Restaurant products | `menus.RestaurantProduct` separate from `agro.Product` | Shared `Product` | Menu items and agro units differ; unification is a future refactor. |
| Orders | One `orders.Order` with `mode` choices | Separate order apps | Shared lifecycle/admin with simple mode split. |
| Order item vendor resolution | `OrderItem` has exactly one of `restaurant_product` or `agro_product` | GenericForeignKey, vendor field | Explicit FKs are admin-friendly, queryable, and reliable for MVP. Validate item FK matches `Order.mode`. |
| Agro units | `Product.Unit` `TextChoices` in `agro/models.py` | Global constants | Unit choices only belong to agro products now. |

## Final Model Definitions

### `accounts.Profile`

Fields: `user OneToOneField(auth.User, CASCADE, related_name='profile')`; `role CharField(max_length=30, choices=Role)` where Role=`consumer, producer, courier, warehouse_manager`, default `consumer`; `phone CharField(max_length=30, blank=True)`; `avatar ImageField(upload_to='profiles/', blank=True)`; `default_address ForeignKey('locations.Address', SET_NULL, null=True, blank=True, related_name='default_for_profiles')`. Index `role`. Validate `default_address.owner == user`. `ordering=['user__username']`. `__str__`: username + role.

### `locations.Address`

Fields: `owner ForeignKey(auth.User, CASCADE, related_name='addresses')`; required `street CharField(150)`, `number CharField(20)`, `city CharField(100)`, `province CharField(100)`; `postal_code CharField(20, blank=True)`; `lat DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)`; `lng DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)`; `is_default BooleanField(default=False)`. Indexes `owner`, `city`. Constraint `UniqueConstraint(fields=['owner'], condition=Q(is_default=True), name='one_default_address_per_user')`. `ordering=['city','street','number']`. `__str__`: street number, city.

### `agro.Producer`

Fields: `profile OneToOneField('accounts.Profile', CASCADE, related_name='producer')`; `business_name CharField(150)`; `tax_id CharField(30, unique=True)`; `address ForeignKey('locations.Address', PROTECT, related_name='producers')`; `description TextField(blank=True)`. Validate profile role `producer`. Index `business_name`. `ordering=['business_name']`. `__str__`: business_name.

### `agro.Product`

Fields: `producer ForeignKey(Producer, CASCADE, related_name='products')`; `name CharField(120)`; `description TextField(blank=True)`; `price DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])`; `unit CharField(max_length=20, choices=Unit)` where Unit=`kg, box, unit`; `is_active BooleanField(default=True)`. Unique constraint `producer,name`. Indexes `producer`, `name`. `ordering=['name']`. `__str__`: name + unit.

### `restaurants.Restaurant`

Fields: `owner ForeignKey(auth.User, CASCADE, related_name='restaurants')`; `name CharField(150)`; `description TextField(blank=True)`; `address ForeignKey('locations.Address', PROTECT, related_name='restaurants')`; `is_active BooleanField(default=True)`. Unique constraint `owner,name`. Index `name`. `ordering=['name']`. `__str__`: name.

### `menus.RestaurantProduct`

Fields: `restaurant ForeignKey('restaurants.Restaurant', CASCADE, related_name='menu_items')`; `name CharField(120)`; `description TextField(blank=True)`; `price DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])`; `is_available BooleanField(default=True)`. Unique constraint `restaurant,name`. Indexes `restaurant`, `name`. `ordering=['restaurant__name','name']`. `__str__`: restaurant + name.

### `orders.Order`

Fields: `consumer ForeignKey(auth.User, PROTECT, related_name='orders')`; `mode CharField(max_length=20, choices=Mode)` where Mode=`restaurant, agro`; `status CharField(max_length=20, choices=Status, default='pending')` where Status=`pending, confirmed, in_delivery, delivered, cancelled`; `delivery_address ForeignKey('locations.Address', PROTECT, related_name='orders')`; `total DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])`; `created_at DateTimeField(auto_now_add=True)`; `updated_at DateTimeField(auto_now=True)`. Indexes `consumer,status,mode,created_at`. Validate address owner matches consumer. `ordering=['-created_at']`. `__str__`: order id + mode + status.

### `orders.OrderItem`

Fields: `order ForeignKey(Order, CASCADE, related_name='items')`; `restaurant_product ForeignKey('menus.RestaurantProduct', PROTECT, null=True, blank=True, related_name='order_items')`; `agro_product ForeignKey('agro.Product', PROTECT, null=True, blank=True, related_name='order_items')`; `quantity DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])`; `unit_price DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])`. Constraint exactly one product FK is non-null. Validate product FK matches `order.mode`. Index `order`. `ordering=['id']`. `__str__`: order + product name.

### `payments.Payment`

Fields: `order OneToOneField('orders.Order', CASCADE, related_name='payment')`; `method CharField(max_length=30, choices=Method)` where Method=`cash, card, transfer, simulated`; `amount DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])`; `status CharField(max_length=20, choices=Status, default='pending')` where Status=`pending, approved, rejected, refunded`; `created_at DateTimeField(auto_now_add=True)`. Index `status`. `ordering=['-created_at']`. `__str__`: order + status.

### `notifications.Notification`

Fields: `user ForeignKey(auth.User, CASCADE, related_name='notifications')`; `type CharField(max_length=30, choices=Type)` where Type=`order, payment, delivery, system`; `message TextField()`; `is_read BooleanField(default=False)`; `created_at DateTimeField(auto_now_add=True)`. Indexes `user,is_read,created_at`. `ordering=['-created_at']`. `__str__`: type + user.

### `delivery.Courier`

Fields: `profile OneToOneField('accounts.Profile', CASCADE, related_name='courier')`; `vehicle_type CharField(max_length=20, choices=Vehicle)` where Vehicle=`bike, motorcycle, car, van`; `license_plate CharField(max_length=20, blank=True)`; `is_available BooleanField(default=False)`; `service_area CharField(max_length=150, blank=True)`. Validate profile role `courier`. Index `is_available`. `ordering=['profile__user__username']`. `__str__`: username + vehicle.

### `delivery.Delivery`

Fields: `order OneToOneField('orders.Order', CASCADE, related_name='delivery')`; `courier ForeignKey(Courier, SET_NULL, null=True, blank=True, related_name='deliveries')`; `status CharField(max_length=20, choices=Status, default='pending')` where Status=`pending, picked_up, in_transit, delivered`; `picked_at DateTimeField(null=True, blank=True)`; `delivered_at DateTimeField(null=True, blank=True)`. Validate order mode `restaurant`. Index `status`. `ordering=['-id']`. `__str__`: delivery + order id.

### `warehouses.Warehouse`

Fields: `producer ForeignKey('agro.Producer', CASCADE, related_name='warehouses')`; `name CharField(120)`; `address ForeignKey('locations.Address', PROTECT, related_name='warehouses')`; `is_active BooleanField(default=True)`. Unique constraint `producer,name`. Index `producer`. `ordering=['name']`. `__str__`: producer + name.

### `inventory.InventoryItem`

Fields: `warehouse ForeignKey('warehouses.Warehouse', CASCADE, related_name='inventory_items')`; `product ForeignKey('agro.Product', CASCADE, related_name='inventory_items')`; `quantity DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])`; `updated_at DateTimeField(auto_now=True)`. Unique constraint `warehouse,product`. Validate warehouse producer equals product producer. Indexes `warehouse`, `product`. `ordering=['warehouse__name','product__name']`. `__str__`: warehouse + product + quantity.

## Settings Changes

Add to `INSTALLED_APPS` after `core`: `accounts`, `locations`, `orders`, `payments`, `notifications`, `restaurants`, `menus`, `delivery`, `agro`, `warehouses`, `inventory`. Do not set `AUTH_USER_MODEL`; use Django default `auth.User`. Add media settings only when avatar uploads are actually served.

## URL Wiring

Current implementation remains: `/` from `core.urls`, `/admin/` from Django admin. Each new app should include an empty/placeholder `urls.py` only when it gains public views. Later top-level routes: `accounts/`, `restaurants/`, `menus/`, `delivery/`, `agro/`, `warehouses/`, `orders/`; admin needs no extra include.

## Admin Registrations

Register: `Profile`, `Address`, `Order`, `OrderItem`, `Payment`, `Notification`, `Restaurant`, `RestaurantProduct`, `Courier`, `Delivery`, `Producer`, `Product`, `Warehouse`, `InventoryItem`.

## Implementation Order

1. Create apps and register settings.
2. Implement `locations` then `accounts`.
3. Implement `agro` products/producers, `restaurants`, `menus`.
4. Implement `orders` with cross-mode item validation.
5. Implement `payments`, `notifications`, `delivery`, `warehouses`, `inventory`.
6. Register admin and create migrations app-by-app.

## Testing Strategy

| Layer | What to Test | Approach |
|---|---|---|
| Model | Role validation, positive prices, default address, product exclusivity | Django `TestCase` model validation |
| Integration | Admin model registration and migrations | `manage.py check`, migration tests |
| E2E | Home/admin availability | Minimal smoke tests |

## Migration / Rollout

No data migration required before implementation. Roll out by app batches; if a batch fails before production data exists, remove app registration and unapplied migrations.

## Risks and Open Questions

- `ImageField` may require Pillow if avatar handling is implemented; use `CharField/URLField` instead if dependency-free avatars are preferred.
- Cross-app validation lives in `clean()` and admin/forms, not only database constraints.
- Future refactor may introduce a shared catalog abstraction, but not for MVP.
