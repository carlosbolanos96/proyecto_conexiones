# Restaurant Mode Specification

## Purpose

Define restaurant catalog and courier delivery behavior for Mode 1.

## Requirements

### Requirement: REST-1 Restaurant catalog

The system MUST let restaurant owners publish restaurants and sell menu products.

Validation: `Restaurant.owner`, `name`, and `address` MUST be required; `description` MAY be blank; each menu product MUST belong to a restaurant; product `name` MUST be required; product `price` MUST be `> 0`.

#### Scenario: Create restaurant product

- GIVEN a restaurant with an owner and address
- WHEN a menu product with name and positive price is saved
- THEN the product is available under that restaurant

#### Scenario: Reject zero price

- GIVEN a restaurant exists
- WHEN a menu product price is `0`
- THEN validation MUST fail

### Requirement: REST-2 Courier profile

The system MUST identify courier profiles and their delivery availability.

Validation: `Courier.profile` MUST be unique and required; profile role MUST be `courier`; `vehicle_type` MUST be an allowed choice; `license_plate` MAY be blank; `is_available` MUST default to false; `service_area` MAY be blank.

#### Scenario: Create courier

- GIVEN a profile with role `courier`
- WHEN courier details are saved
- THEN the courier can be marked available for delivery

#### Scenario: Reject non-courier profile

- GIVEN a profile with role `consumer`
- WHEN courier details are saved
- THEN validation MUST fail

### Requirement: REST-3 Restaurant delivery lifecycle

The system MUST track one delivery per order with courier and delivery status.

Validation: `Delivery.order` MUST be unique and required; `courier` MAY be null while pending; status MUST be `pending`, `picked_up`, `in_transit`, or `delivered`; `picked_at` and `delivered_at` MAY be null until their statuses occur.

#### Scenario: Assign courier delivery

- GIVEN a restaurant order in status `confirmed`
- WHEN an available courier is assigned
- THEN delivery is linked to the order
- AND status can progress toward `delivered`

### Requirement: REST-4 Restaurant admin

The system MUST expose `Restaurant`, menu product model, `Courier`, and `Delivery` in Django admin.

#### Scenario: Staff manages restaurant mode

- GIVEN staff is logged in to `/admin`
- WHEN they open restaurant mode apps
- THEN catalog and delivery records are visible and editable

## Files/Key Objects

- `restaurants/models.py`: `Restaurant(owner FK, name, description, address)`.
- `menus/models.py`: `RestaurantProduct(restaurant FK, name, price)` or equivalent menu product object.
- `delivery/models.py`: `Courier`, `Delivery`.
- Matching `admin.py` files register every model above.
