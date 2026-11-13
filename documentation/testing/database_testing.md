
# SokoCater Database Testing Documentation

## 1. Introduction

This document describes the testing procedures for the SokoCater database.

The purpose of database testing is to ensure that information is stored correctly, relationships work as expected and database constraints maintain data integrity.

## 2. Database Testing Objectives

- Verify that database tables are created correctly.
- Verify primary and foreign key relationships.
- Check that required fields cannot be left empty.
- Verify that unique constraints work.
- Check that booking records are associated with the correct customers and caterers.
- Verify that payments are associated with bookings.
- Check that the database prevents conflicting confirmed bookings.

## 3. Test Cases

| Test ID | Test Description | Expected Result |
|---|---|---|
| DB01 | Create a new user | User is saved successfully |
| DB02 | Register with an existing email | Duplicate email is rejected |
| DB03 | Create a caterer profile | Profile is associated with its user |
| DB04 | Add a menu to a caterer | Menu is saved successfully |
| DB05 | Add a menu item | Item is associated with its menu |
| DB06 | Create a catering package | Package is saved successfully |
| DB07 | Add items to a package | Package items are linked correctly |
| DB08 | Create a booking | Booking is associated with the correct customer and caterer |
| DB09 | Submit an invalid guest count | Invalid booking is rejected |
| DB10 | Record a deposit payment | Payment is associated with its booking |
| DB11 | Submit a rating outside 1–5 | Invalid rating is rejected |
| DB12 | Create duplicate availability for a date | Duplicate record is rejected |
| DB13 | Confirm conflicting bookings | Only one booking for the caterer and date can be confirmed |

## 4. Testing Tools

The following tools will be used:

- Flask-SQLAlchemy: Database operations and ORM.
- SQLite or PostgreSQL: Database storage.
- Postman: API endpoint testing.
- Pytest: Automated backend testing.

## 5. Expected Testing Results

The database should:

1. Store valid user and business information.
2. Maintain relationships between all related tables.
3. Reject duplicate email addresses.
4. Reject invalid records.
5. Correctly associate bookings with customers and caterers.
6. Store payment information against the correct booking.
7. Prevent conflicting confirmed bookings.

## 6. Conclusion

Database testing will help ensure that the SokoCater platform stores accurate information, maintains data integrity and supports the application's main booking operations.

Actual test results will be recorded after the database models and backend APIs have been implemented.
