# Account Roles Specification

## Purpose

Define a single Django user model with role-based profiles for the dual-mode platform.

## Requirements

### Requirement: ACCT-1 User profile roles

The system MUST maintain one `Profile` per Django `User` and MUST classify each profile with exactly one role: `consumer`, `producer`, `courier`, or `warehouse_manager`.

Validation: `user` MUST be unique and required; `role` MUST be one of the allowed choices; `phone` MAY be blank; `avatar` MAY be blank; `default_address` MAY be null and MUST reference an address owned by the same user when set.

#### Scenario: Create role profile

- GIVEN an existing Django user without a profile
- WHEN a profile is created with role `producer`
- THEN the profile is stored for that user
- AND no second profile can be created for the same user

#### Scenario: Reject invalid role

- GIVEN an existing Django user
- WHEN a profile is submitted with role `seller`
- THEN validation MUST fail

### Requirement: ACCT-2 Profile admin management

The system MUST expose `Profile` in Django admin so staff can view and edit role, phone, avatar, and default address.

#### Scenario: Staff manages profiles

- GIVEN staff is logged in to `/admin`
- WHEN they open the accounts section
- THEN `Profile` records are visible and editable

## Files/Key Objects

- `accounts/models.py`: `Profile(user OneToOne, role, phone, avatar, default_address FK)`.
- `accounts/admin.py`: registers `Profile`.
- `accounts/apps.py`: Django app config.
