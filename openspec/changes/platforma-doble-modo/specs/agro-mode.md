# Agro Mode Specification

## Purpose

Define producer, product, warehouse, and inventory behavior for Mode 2.

## Requirements

### Requirement: AGRO-1 Producer profile

The system MUST let producer profiles define agro business data.

Validation: `Producer.profile` MUST be unique and required; profile role MUST be `producer`; `business_name`, `tax_id`, and `address` MUST be required; `description` MAY be blank.

#### Scenario: Create producer

- GIVEN a profile with role `producer`
- WHEN required producer data is saved
- THEN a producer business record is available

#### Scenario: Reject wrong role

- GIVEN a profile with role `consumer`
- WHEN producer data is saved
- THEN validation MUST fail

### Requirement: AGRO-2 Agro products

The system MUST let producers publish products sold by quantity and unit.

Validation: `producer`, `name`, `price`, and `unit` MUST be required; `description` MAY be blank; `price` MUST be `> 0`; `unit` MUST identify the sale unit such as kg, box, or unit.

#### Scenario: Publish agro product

- GIVEN an existing producer
- WHEN a product with positive price and unit is saved
- THEN it can be used in agro order items

### Requirement: AGRO-3 Warehouses and inventory

The system MUST store producer warehouses and product stock per warehouse.

Validation: `Warehouse.producer`, `name`, and `address` MUST be required; `InventoryItem.warehouse` and `product` MUST be required; `quantity` MUST be `>= 0`; each product SHOULD appear once per warehouse.

#### Scenario: Track stock

- GIVEN a warehouse and product from the same producer
- WHEN inventory quantity is saved as `10`
- THEN available stock is recorded for that warehouse

#### Scenario: Reject negative stock

- GIVEN a warehouse and product exist
- WHEN inventory quantity is `-1`
- THEN validation MUST fail

### Requirement: AGRO-4 Agro admin

The system MUST expose `Producer`, `Product`, `Warehouse`, and `InventoryItem` in Django admin.

#### Scenario: Staff manages agro data

- GIVEN staff is logged in to `/admin`
- WHEN they open agro mode apps
- THEN producer, product, warehouse, and inventory records are visible and editable

## Files/Key Objects

- `agro/models.py`: `Producer`, `Product`.
- `warehouses/models.py`: `Warehouse`.
- `inventory/models.py`: `InventoryItem`.
- Matching `admin.py` files register every model above.
