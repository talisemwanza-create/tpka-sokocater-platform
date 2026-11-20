# SokoCater Platform: User Stories

User stories describe what each type of user needs from SokoCater and why. Each story has:

- **ID** for tracking (use it as the GitHub issue title prefix, e.g. `US-07: Create a booking`)
- **Story** in the form *As a [role], I want [goal], so that [benefit]*
- **Acceptance criteria**: the checklist that must be true for the story to be "done"
- **Priority** using MoSCoW: **Must** (core), **Should** (important), **Could** (nice to have)

---

## Roles

| Role | Description |
|------|-------------|
| **Visitor** | Anyone browsing without an account |
| **Customer** | Registered user who books catering for an event |
| **Caterer** | Registered business owner who offers catering services |
| **Admin** | Platform administrator who verifies caterers and moderates content |

---

## 1. Accounts & Authentication

### US-01: Sign up
**As a** visitor, **I want** to create an account as a customer or a caterer, **so that** I can use the platform.
- [ ] I can register with full name, email, phone and password
- [ ] I choose whether I'm a customer or a caterer (I can't choose admin)
- [ ] Email must be unique; a duplicate shows a clear error
- [ ] My password is stored hashed, never as plain text

**Priority:** Must

### US-02: Log in
**As a** registered user, **I want** to log in with my email and password, **so that** I can access my account.
- [ ] A correct email and password logs me in and returns a token
- [ ] A wrong password shows an error without revealing which field was wrong
- [ ] After login I'm taken to the page for my role

**Priority:** Must

### US-03: Log out
**As a** logged-in user, **I want** to log out, **so that** my account stays secure on shared devices.
- [ ] Logging out clears my session or token
- [ ] Protected pages are no longer accessible after logging out

**Priority:** Should

---

## 2. Customer Stories

### US-04: Browse caterers
**As a** visitor or customer, **I want** to see a list of caterers, **so that** I can discover who is available.
- [ ] The list shows business name, location, cuisines and rating
- [ ] Only verified or active caterers are shown
- [ ] The list loads without needing an account

**Priority:** Must

### US-05: Search and filter caterers
**As a** customer, **I want** to filter caterers by location, cuisine and price range, **so that** I find options that fit my event and budget.
- [ ] I can filter by at least location, cuisine and maximum price
- [ ] Filters can be combined
- [ ] If nothing matches, I see a "no results" message

**Priority:** Must

### US-06: View a caterer's profile and menu
**As a** customer, **I want** to view a caterer's details, menu items and reviews, **so that** I can compare offers before booking.
- [ ] The profile shows description, location, cuisines and verification status
- [ ] The menu lists each item with description and price per person
- [ ] Reviews and the average rating are visible

**Priority:** Must

### US-07: Create a booking
**As a** customer, **I want** to book a caterer for a specific date and guest count, **so that** I can secure catering for my event.
- [ ] I choose a caterer, event date, event type and number of guests
- [ ] I can select menu items for the booking
- [ ] I can't book a date in the past
- [ ] The booking is created with status `pending`
- [ ] I see a confirmation message after submitting

**Priority:** Must

### US-08: View my bookings
**As a** customer, **I want** to see all my bookings and their status, **so that** I can track my events.
- [ ] I see only my own bookings
- [ ] Each shows caterer, date, guest count and status (pending, confirmed, cancelled, completed)

**Priority:** Must

### US-09: Cancel a booking
**As a** customer, **I want** to cancel a booking, **so that** I can change my plans.
- [ ] I can cancel my own `pending` or `confirmed` bookings
- [ ] The status changes to `cancelled`
- [ ] I can't cancel a `completed` booking or someone else's booking

**Priority:** Should

### US-10: Review a caterer
**As a** customer, **I want** to rate and review a caterer after my event, **so that** other customers can make informed choices.
- [ ] I can only review a booking marked `completed`
- [ ] I can leave a rating from 1 to 5 and an optional comment
- [ ] I can review each booking only once

**Priority:** Should

---

## 3. Caterer Stories

### US-11: Create a business profile
**As a** caterer, **I want** to create my business profile, **so that** customers can find me.
- [ ] I can enter business name, description and location
- [ ] I can select the cuisines I serve
- [ ] Only I (or an admin) can edit my profile

**Priority:** Must

### US-12: Manage menu items
**As a** caterer, **I want** to add, edit and delete menu items with prices, **so that** my offers stay up to date.
- [ ] I can add an item with name, description and price per person
- [ ] I can edit and delete only my own items
- [ ] Price can't be negative

**Priority:** Must

### US-13: View booking requests
**As a** caterer, **I want** to see booking requests I've received, **so that** I can respond to customers.
- [ ] I see only bookings made for my business
- [ ] Each shows customer, date, guest count, selected items and status

**Priority:** Must

### US-14: Accept or decline a booking
**As a** caterer, **I want** to accept or decline booking requests, **so that** I can manage my schedule.
- [ ] I can change a `pending` booking to `confirmed` or `cancelled`
- [ ] I can mark a confirmed booking as `completed` after the event
- [ ] I can't change bookings that belong to other caterers

**Priority:** Must

### US-15: See upcoming events
**As a** caterer, **I want** to see my confirmed upcoming events in date order, **so that** I can plan ahead.
- [ ] Confirmed future bookings are listed soonest first
- [ ] Past events are separated from upcoming ones

**Priority:** Should

---

## 4. Admin Stories

### US-16: View all users
**As an** admin, **I want** to see all registered users and their roles, **so that** I can oversee the platform.
- [ ] I can see a list of users with name, email and role
- [ ] Non-admins can't access this list (they get a `403`)

**Priority:** Should

### US-17: Verify caterers
**As an** admin, **I want** to verify caterers, **so that** customers can trust the listings.
- [ ] I can mark a caterer as verified
- [ ] Verified status shows on the caterer's profile
- [ ] Only admins can verify

**Priority:** Should

### US-18: Moderate reviews
**As an** admin, **I want** to remove inappropriate reviews, **so that** the platform stays fair and respectful.
- [ ] I can delete any review
- [ ] The caterer's average rating updates after deletion

**Priority:** Could

### US-19: Manage user roles
**As an** admin, **I want** to change a user's role, **so that** I can fix mistakes or promote trusted users.
- [ ] I can change a user's role between customer, caterer and admin
- [ ] Non-admins can't change roles

**Priority:** Could

---

## 5. Security & Access Control

### US-20: Role-based access
**As a** platform owner, **I want** every action restricted to the right role, **so that** users can only do what they're allowed to.
- [ ] Requests without a valid token get `401 Unauthorized`
- [ ] Requests from the wrong role get `403 Forbidden`
- [ ] Users can only change their own data (ownership checks)
- [ ] Public signup can't create an admin account

**Priority:** Must

---

## 6. Sprint 1 Enabler Stories (Foundation)

These support the team rather than end users, but they are needed for Milestone Gate 1.

### E-01: Local development environment
**As a** developer, **I want** a working local setup for backend and frontend, **so that** the whole team can build and run the app.
- [ ] README setup steps work on a fresh machine
- [ ] Flask and React both start locally

**Priority:** Must

### E-02: Health check endpoint
**As a** developer, **I want** a `/api/health` endpoint, **so that** we can confirm the API is running.
- [ ] `GET /api/health` returns `200 OK`

**Priority:** Must

### E-03: Database schema
**As a** developer, **I want** an approved database schema and ERD, **so that** the backend models are built on a solid design.
- [ ] ERD is reviewed and approved by the team
- [ ] SQLAlchemy models connect to the database

**Priority:** Must

### E-04: Wireframes
**As a** team, **we want** wireframes for the main screens, **so that** the React frontend follows an agreed design.
- [ ] Wireframes cover home, caterer list, caterer profile, booking and dashboards
- [ ] Link is added to the README

**Priority:** Must

### E-05: Repository and project board
**As a** team, **we want** a GitHub repository and a project board with the initial backlog, **so that** work is organized and visible.
- [ ] Board has To Do / In Progress / Done columns
- [ ] User stories are added as issues

**Priority:** Must

---

## Summary

| Priority | Stories |
|----------|---------|
| **Must** | US-01, US-02, US-04, US-05, US-06, US-07, US-08, US-11, US-12, US-13, US-14, US-20, E-01 to E-05 |
| **Should** | US-03, US-09, US-10, US-15, US-16, US-17 |
| **Could** | US-18, US-19 |