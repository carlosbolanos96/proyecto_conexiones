# Shared Commerce Specification

## Purpose

Define shared addresses, orders, payments, and notifications reused by restaurant and agro modes.

## Requirements

### Requirement: COMM-1 Customer addresses

The system MUST let users store delivery addresses with optional coordinates and one default address.

Validation: `owner`, `street`, `number`, `city`, and `province` MUST be required; `postal_code` MAY be blank; `lat` and `lng` MAY be null; only one address per user SHOULD be marked `is_default`.

#### Scenario: Store address

- GIVEN an authenticated user
- WHEN an address with required fields is saved
- THEN it is linked to that user

#### Scenario: Reject incomplete address

- GIVEN an authenticated user
- WHEN `city` is missing
- THEN validation MUST fail

### Requirement: COMM-2 Orders and items

The system MUST store orders with consumer, mode, status, delivery address, total, and line items.

Validation: `consumer`, `mode`, `status`, `delivery_address`, `total` MUST be required; `mode` MUST be `restaurant` or `agro`; `status` MUST be `pending`, `confirmed`, `in_delivery`, `delivered`, or `cancelled`; `total` MUST be `>= 0`; item `quantity` and `unit_price` MUST be `> 0`.

#### Scenario: Create pending order

- GIVEN a consumer with a valid address
- WHEN an order with at least one item is created
- THEN status defaults to `pending`
- AND total represents item quantities and prices

#### Scenario: Reject invalid order mode

- GIVEN a consumer with a valid address
- WHEN an order uses mode `pharmacy`
- THEN validation MUST fail

### Requirement: COMM-3 Simulated payments

The system MUST store one simulated payment per order.

Validation: `order` MUST be unique and required; `method`, `amount`, and `status` MUST be required; `amount` MUST be `> 0`; status MUST represent simulated payment state.

#### Scenario: Register simulated payment

- GIVEN an existing order
- WHEN a payment is saved for the order total
- THEN staff can see payment method, amount, and status

### Requirement: COMM-4 User notifications

The system MUST store notifications addressed to a user.

Validation: `user`, `type`, and `message` MUST be required; `is_read` MUST default to false.

#### Scenario: Create unread notification

- GIVEN an order status changes
- WHEN a notification is created
- THEN it is unread until explicitly marked read

### Requirement: COMM-5 Shared commerce admin

The system MUST expose `Address`, `Order`, `OrderItem`, `Payment`, and `Notification` in Django admin.

#### Scenario: Staff audits commerce data

- GIVEN staff is logged in to `/admin`
- WHEN they open shared commerce apps
- THEN the listed models are visible and editable

## Files/Key Objects

- `locations/models.py`: `Address`.
- `orders/models.py`: `Order`, `OrderItem`.
- `payments/models.py`: `Payment`.
- `notifications/models.py`: `Notification`.
- Matching `admin.py` files register every model above.
