
# SokoCater Database Schema Documentation

## 1. Introduction

The SokoCater platform is a web-based catering service discovery and booking system that connects customers with catering service providers.

The database is designed to store and manage information about users, catering businesses, menus, food items, catering packages, bookings, availability, payments, reviews and notifications.

The proposed database uses a relational database structure with primary keys and foreign keys to maintain data integrity and establish relationships between entities.

## 2. Database Objectives

The main objectives of the database are:

1. Store customer, caterer and administrator account information.
2. Manage catering business profiles.
3. Store catering menus and individual food items.
4. Manage catering packages and additional services.
5. Record customer booking requests.
6. Track caterer availability and prevent double bookings.
7. Record deposit payments.
8. Store customer reviews and ratings.
9. Manage booking notifications and reminders.

## 3. Proposed Database Tables

The database consists of the following 13 tables.

### 3.1 Users

Stores information about registered platform users.

| Attribute | Data Type | Constraint |
|---|---|---|
| id | Integer | Primary Key |
| full_name | String(100) | NOT NULL |
| email | String(120) | UNIQUE, NOT NULL |
| password_hash | String(255) | NOT NULL |
| role | String(20) | NOT NULL |
| phone_number | String(20) | |
| created_at | DateTime | NOT NULL |

User roles include customer, caterer and admin.

### 3.2 CatererProfiles

Stores catering business information.

| Attribute | Data Type | Constraint |
|---|---|---|
| id | Integer | Primary Key |
| user_id | Integer | Foreign Key, UNIQUE |
| business_name | String(150) | NOT NULL |
| description | Text | |
| location | String(150) | NOT NULL |
| contact_number | String(20) | |
| business_image | String(255) | |
| verification_status | String(20) | NOT NULL |
| created_at | DateTime | NOT NULL |

The user_id references Users.id.

### 3.3 Menus

Stores menus created by caterers.

| Attribute | Data Type | Constraint |
|---|---|---|
| id | Integer | Primary Key |
| caterer_id | Integer | Foreign Key |
| menu_name | String(100) | NOT NULL |
| description | Text | |
| created_at | DateTime | NOT NULL |

The caterer_id references CatererProfiles.id.

### 3.4 MenuItems

Stores individual food items belonging to menus.

| Attribute | Data Type | Constraint |
|---|---|---|
| id | Integer | Primary Key |
| menu_id | Integer | Foreign Key |
| item_name | String(100) | NOT NULL |
| description | Text | |
| price | Decimal(10,2) | NOT NULL |
| image_url | String(255) | |

The menu_id references Menus.id.

### 3.5 Packages

Stores catering packages offered by caterers.

| Attribute | Data Type | Constraint |
|---|---|---|
| id | Integer | Primary Key |
| caterer_id | Integer | Foreign Key |
| package_name | String(100) | NOT NULL |
| description | Text | |
| price_per_guest | Decimal(10,2) | NOT NULL |
| minimum_guests | Integer | NOT NULL |
| maximum_guests | Integer | |

The caterer_id references CatererProfiles.id.

### 3.6 PackageItems

Connects catering packages to their included menu items.

| Attribute | Data Type | Constraint |
|---|---|---|
| id | Integer | Primary Key |
| package_id | Integer | Foreign Key |
| menu_item_id | Integer | Foreign Key |

The package_id references Packages.id.

The menu_item_id references MenuItems.id.

A unique constraint should be applied to the combination of package_id and menu_item_id to prevent duplicate items within the same package.

### 3.7 AddOns

Stores optional additional catering services.

| Attribute | Data Type | Constraint |
|---|---|---|
| id | Integer | Primary Key |
| caterer_id | Integer | Foreign Key |
| addon_name | String(100) | NOT NULL |
| description | Text | |
| price | Decimal(10,2) | NOT NULL |

Examples include delivery, serving staff, tables, chairs and catering equipment.

The caterer_id references CatererProfiles.id.

### 3.8 Bookings

Stores customer catering booking information.

| Attribute | Data Type | Constraint |
|---|---|---|
| id | Integer | Primary Key |
| customer_id | Integer | Foreign Key |
| caterer_id | Integer | Foreign Key |
| event_date | Date | NOT NULL |
| event_type | String(100) | NOT NULL |
| event_location | String(200) | NOT NULL |
| guest_count | Integer | NOT NULL |
| estimated_total | Decimal(10,2) | NOT NULL |
| status | String(20) | NOT NULL |
| created_at | DateTime | NOT NULL |

The customer_id references Users.id.

The caterer_id references CatererProfiles.id.

Booking statuses include pending, accepted, rejected, confirmed, cancelled and completed.

### 3.9 BookingItems

Stores packages and additional services selected for a booking.

| Attribute | Data Type | Constraint |
|---|---|---|
| id | Integer | Primary Key |
| booking_id | Integer | Foreign Key |
| package_id | Integer | Foreign Key, Nullable |
| addon_id | Integer | Foreign Key, Nullable |
| quantity | Integer | NOT NULL |
| unit_price | Decimal(10,2) | NOT NULL |

The booking_id references Bookings.id.

The package_id references Packages.id.

The addon_id references AddOns.id.

Each booking item must reference either a package or an add-on, but not both.

### 3.10 Availability

Stores caterer availability information.

| Attribute | Data Type | Constraint |
|---|---|---|
| id | Integer | Primary Key |
| caterer_id | Integer | Foreign Key |
| available_date | Date | NOT NULL |
| status | String(20) | NOT NULL |

The caterer_id references CatererProfiles.id.

Availability statuses include available, unavailable and booked.

A unique constraint should be applied to caterer_id and available_date.

### 3.11 Payments

Stores customer deposit and payment information.

| Attribute | Data Type | Constraint |
|---|---|---|
| id | Integer | Primary Key |
| booking_id | Integer | Foreign Key |
| amount | Decimal(10,2) | NOT NULL |
| payment_method | String(50) | NOT NULL |
| transaction_reference | String(100) | UNIQUE |
| payment_status | String(20) | NOT NULL |
| paid_at | DateTime | |

Payment statuses include pending, successful and failed.

### 3.12 Reviews

Stores customer feedback and ratings for catering businesses.

| Attribute | Data Type | Constraint |
|---|---|---|
| id | Integer | Primary Key |
| customer_id | Integer | Foreign Key |
| caterer_id | Integer | Foreign Key |
| booking_id | Integer | Foreign Key |
| rating | Integer | NOT NULL |
| comment | Text | |
| created_at | DateTime | NOT NULL |

The customer_id references Users.id.

The caterer_id references CatererProfiles.id.

The booking_id references Bookings.id.

Ratings must be between 1 and 5. Each completed booking should have at most one review.

### 3.13 Notifications

Stores notifications sent to platform users.

| Attribute | Data Type | Constraint |
|---|---|---|
| id | Integer | Primary Key |
| user_id | Integer | Foreign Key |
| message | Text | NOT NULL |
| notification_type | String(50) | NOT NULL |
| is_read | Boolean | NOT NULL |
| created_at | DateTime | NOT NULL |

The user_id references Users.id.

## 4. Database Relationships

The database contains the following relationships:

| Relationship | Cardinality |
|---|---|
| Users to CatererProfiles | One-to-One (optional for users) |
| CatererProfiles to Menus | One-to-Many |
| Menus to MenuItems | One-to-Many |
| CatererProfiles to Packages | One-to-Many |
| Packages to PackageItems | One-to-Many |
| MenuItems to PackageItems | One-to-Many |
| CatererProfiles to AddOns | One-to-Many |
| Users to Bookings | One-to-Many |
| CatererProfiles to Bookings | One-to-Many |
| Bookings to BookingItems | One-to-Many |
| Packages to BookingItems | One-to-Many |
| AddOns to BookingItems | One-to-Many |
| CatererProfiles to Availability | One-to-Many |
| Bookings to Payments | One-to-Many |
| Users to Reviews | One-to-Many |
| CatererProfiles to Reviews | One-to-Many |
| Users to Notifications | One-to-Many |

## 5. Database Constraints

The following constraints will help maintain data accuracy and consistency:

- Primary keys uniquely identify every record.
- Foreign keys maintain relationships between tables.
- Email addresses must be unique.
- User passwords must be securely hashed.
- Required attributes must not contain NULL values.
- Package prices and payment amounts must not be negative.
- Guest counts must be positive.
- Ratings must be between 1 and 5.
- Booking and payment statuses must use valid values.
- A caterer should not have duplicate availability records for the same date.
- A completed booking can have at most one review.

## 6. Database Security

The database will implement the following security measures:

1. Passwords will be hashed before storage.
2. Role-based access control will restrict access to customer, caterer and administrator functions.
3. Foreign key constraints will maintain referential integrity.
4. Sensitive payment information will be handled securely.
5. Database queries will use parameterized ORM operations to reduce SQL injection risks.
6. Users will only be permitted to access resources they are authorized to manage.

## 7. Booking and Availability Management

The booking process will follow these steps:

1. A customer selects a caterer.
2. The customer selects a package and additional services.
3. The customer enters the event date and guest count.
4. The system checks caterer availability.
5. The system calculates the estimated booking cost.
6. The customer submits a booking request.
7. The caterer accepts or rejects the request.
8. The customer proceeds with the deposit payment.
9. The payment is verified.
10. The booking becomes confirmed and the date is locked.

The system will use backend validation and database transactions to prevent two customers from confirming the same caterer for the same event date.

## 8. Conclusion

The proposed SokoCater database schema provides a structured way of managing the platform's information.

The database supports user management, caterer profiles, menu management, catering packages, booking requests, availability tracking, payment records, reviews and notifications.

The schema will serve as the foundation for implementing the database using Flask-SQLAlchemy and integrating it with the React frontend.
