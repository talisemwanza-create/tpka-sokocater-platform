<div align="center">

# 🍽️ SokoCater Platform

**A full-stack catering booking platform that connects customers with caterers across Kenya: find, compare, and book the right caterer for any event.**

![React](https://img.shields.io/badge/frontend-React-61DAFB?logo=react&logoColor=white)
![Flask](https://img.shields.io/badge/backend-Flask-000000?logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![Auth](https://img.shields.io/badge/auth-JWT%20%2B%20RBAC-green)
![Status](https://img.shields.io/badge/status-in%20development-orange)

[Live Demo](#) · [Project Board](#) · [Report a Bug](../../issues)

</div>

---

## 📖 Table of Contents

1. [About the Project](#-about-the-project)
2. [Problem Statement](#-problem-statement)
3. [Key Features](#-key-features)
4. [User Roles & Stories](#-user-roles--stories)
5. [Authentication & Access Control (IAM)](#-authentication--access-control-iam)
6. [Tech Stack](#-tech-stack)
7. [System Architecture](#-system-architecture)
8. [Database Design](#-database-design)
9. [Getting Started](#-getting-started)
10. [Environment Variables](#-environment-variables)
11. [API Reference](#-api-reference)
12. [Project Structure](#-project-structure)
13. [Testing](#-testing)
14. [Team & Workflow](#-team--workflow)
15. [Roadmap](#-roadmap)
16. [Contributing](#-contributing)
17. [License](#-license)

---

## 🌍 About the Project

**SokoCater Platform** (*"soko"* meaning *market* in Swahili) is a full-stack web application where customers can discover caterers, browse menus and packages, check availability, and book catering for weddings, corporate events, birthdays, funerals, and other gatherings across Kenya, all in one place.

Caterers get a digital storefront to showcase their services and manage bookings. Administrators keep the platform trustworthy by verifying caterers and moderating content.

The project is a group capstone built with a **React** front end, a **Flask** REST API, a **PostgreSQL** database, and **role-based authentication** with multiple access levels.

---

## 🎯 Problem Statement

Booking a caterer today is fragmented and time-consuming:

- **Customers** struggle to find reliable caterers, compare prices and menus, and confirm availability.
- **Caterers** rely on phone calls, WhatsApp, and paper records, which leads to double bookings, missed inquiries, and poor visibility.
- There is **no single, trusted platform** that handles discovery, booking, and communication end to end.

**SokoCater solves this** with a centralized platform for discovery, booking, and management of catering services, secured by role-based access so each type of user only sees and does what they should.

---

## ✨ Key Features

### For Customers
- 🔍 Search and filter caterers by location, cuisine, price range, and event type
- 📋 View caterer profiles, menus, packages, and reviews
- 📅 Book for a specific date and guest count
- 💬 Track booking status (pending, confirmed, cancelled, completed)
- ⭐ Leave ratings and reviews after an event

### For Caterers
- 🏪 Create and manage a business profile
- 🍲 Add and update menus, packages, and pricing
- 🗓️ Accept or decline booking requests
- 📊 View booking history and upcoming events

### For Admins
- 👥 Manage users and caterer accounts
- ✅ Verify and approve caterers
- 🛡️ Moderate reviews and monitor platform activity

---

## 👤 User Roles & Stories

| Role | Example User Stories |
|------|----------------------|
| **Customer** | As a customer, I want to search for caterers by location and budget so that I can find options that fit my event. |
| **Customer** | As a customer, I want to book a caterer for a specific date so that I can secure my event catering. |
| **Caterer** | As a caterer, I want to list my menus and packages so that customers can see what I offer. |
| **Caterer** | As a caterer, I want to accept or decline booking requests so that I can manage my schedule. |
| **Admin** | As an admin, I want to verify caterers so that customers can trust the platform. |

> 📌 The full list of user stories, with acceptance criteria and priorities, is in [`docs/user-stories.md`](docs/user-stories.md) and tracked on our GitHub Projects board. *(Add board link here)*

---

## 🔐 Authentication & Access Control (IAM)

SokoCater implements **Identity and Access Management** with two layers: *authentication* (who are you?) and *authorization* (what are you allowed to do?).

### Authentication

- Users **sign up and log in** with email and password.
- Passwords are **hashed with bcrypt**. Plain-text passwords are never stored.
- On login, the API issues a signed **JSON Web Token (JWT)**. The React app sends it in the `Authorization: Bearer <token>` header on protected requests.
- Tokens **expire** after a set time, after which the user must log in again.

### Authorization: Role-Based Access Control (RBAC)

Every user has exactly one role, stored in `users.role`:

| Role | Description | How it's assigned |
|------|-------------|-------------------|
| `customer` | Searches caterers and makes bookings | Default on signup |
| `caterer` | Manages their own business, menus, and bookings | Chosen at signup; can be verified by an admin |
| `admin` | Manages users, verifies caterers, moderates reviews | Created via seed script only, never through public signup |

### Permissions matrix

| Action | Public | Customer | Caterer | Admin |
|--------|:------:|:--------:|:-------:|:-----:|
| Browse caterers and menus | ✅ | ✅ | ✅ | ✅ |
| Sign up / log in | ✅ | ✅ | ✅ | ✅ |
| Create a booking | ❌ | ✅ | ❌ | ❌ |
| View own bookings | ❌ | ✅ | ✅ (received) | ✅ (all) |
| Cancel own booking | ❌ | ✅ | ❌ | ✅ |
| Accept / decline a booking | ❌ | ❌ | ✅ (own only) | ✅ |
| Create / edit own caterer profile | ❌ | ❌ | ✅ | ✅ |
| Add / edit / delete own menu items | ❌ | ❌ | ✅ | ✅ |
| Leave a review (after a completed booking) | ❌ | ✅ | ❌ | ❌ |
| Verify a caterer | ❌ | ❌ | ❌ | ✅ |
| Manage users and roles | ❌ | ❌ | ❌ | ✅ |
| Delete inappropriate reviews | ❌ | ❌ | ❌ | ✅ |

### How access is enforced

- **Backend (the source of truth):**
  - A `@jwt_required()` check protects private routes.
  - A custom `@role_required("caterer")` decorator restricts routes by role and returns `401 Unauthorized` (not logged in) or `403 Forbidden` (wrong role).
  - **Ownership checks:** a caterer can only edit their own menus and bookings, and a customer can only see their own bookings.
- **Frontend (for user experience only):** protected routes and role-based dashboards hide pages that a user can't use. The frontend is *not* trusted for security; the API always re-checks.
- **Admin accounts** can't be self-registered. They are created through the seed script.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React, React Router |
| **Backend** | Python, Flask, Flask-SQLAlchemy, Flask-Migrate (Alembic), Flask-CORS |
| **Database** | **PostgreSQL** (via `psycopg2`) |
| **Authentication & IAM** | Flask-JWT-Extended (JWT), Flask-Bcrypt, role-based access control |
| **Version Control** | Git & GitHub (Issues, Pull Requests) |
| **Project Management** | Scrum with GitHub Projects |

---

## 🏗️ System Architecture

```
┌──────────────┐   HTTP/JSON + JWT   ┌────────────────┐     SQL     ┌──────────────┐
│   Frontend   │  ◄───────────────►  │    Backend     │  ◄───────►  │  PostgreSQL  │
│   (React)    │                     │  (Flask REST)  │             │   Database   │
└──────────────┘                     └────────────────┘             └──────────────┘
                                       │ Auth: JWT + bcrypt
                                       │ Access: role checks (RBAC)
```

The React app consumes a RESTful API exposed by Flask. Every protected request carries a JWT; the API verifies the token, checks the user's role and ownership, then reads or writes PostgreSQL through SQLAlchemy.

---

## 🗄️ Database Design

The PostgreSQL schema is normalized to **Third Normal Form (3NF)** to reduce redundancy and keep data consistent.

**Core entities:**

| Entity | Description |
|--------|-------------|
| `users` | Account details, hashed password, and role (customer, caterer, admin) |
| `caterers` | Business profile linked to a user |
| `menu_items` | Food offerings and pricing from a caterer |
| `bookings` | A customer's reservation of a caterer for an event |
| `booking_items` | Junction table: menu items included in a booking |
| `cuisines` | Cuisine categories (e.g. Swahili, Continental) |
| `caterer_cuisines` | Junction table: cuisines a caterer serves |
| `reviews` | Customer rating and feedback tied to a booking |

**Key relationships:**
- A **User** can have one **Caterer** profile (if they register as a caterer).
- A **Caterer** has many **Menu Items** and receives many **Bookings**.
- A **Customer** makes many **Bookings**; each **Booking** belongs to one **Caterer**.
- **Bookings ↔ Menu Items** and **Caterers ↔ Cuisines** are many-to-many (via junction tables).
- A **Booking** can have one **Review**.

```mermaid
erDiagram
    USERS ||--o| CATERERS : "owns profile"
    USERS ||--o{ BOOKINGS : "makes"
    CATERERS ||--o{ MENU_ITEMS : "offers"
    CATERERS ||--o{ BOOKINGS : "receives"
    BOOKINGS ||--o{ BOOKING_ITEMS : "contains"
    MENU_ITEMS ||--o{ BOOKING_ITEMS : "included in"
    CATERERS ||--o{ CATERER_CUISINES : "serves"
    CUISINES ||--o{ CATERER_CUISINES : "tagged as"
    BOOKINGS ||--o| REVIEWS : "gets"
```

📄 **Team schema documentation (source of truth):**
- Schema: [`documentation/database/database_schema.md`](documentation/database/database_schema.md)
- ER diagram: [`documentation/diagrams/SokoCater_ER_Diagram.mmd`](documentation/diagrams/SokoCater_ER_Diagram.mmd)
- Database testing: [`documentation/testing/database_testing.md`](documentation/testing/database_testing.md)

📄 Additional ERD overview, data dictionary and normalization walkthrough: [`docs/database-design.md`](docs/database-design.md).

---

## 🚀 Getting Started

### Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/) and npm
- [PostgreSQL 14+](https://www.postgresql.org/download/)
- [Git](https://git-scm.com/)
- [Pipenv](https://pipenv.pypa.io/) (or `venv`)

### 1. Clone the repository

```bash
git clone https://github.com/talisemwanza-create/tpka-sokocater-platform.git
cd tpka-sokocater-platform
```

### 2. Create the PostgreSQL database

```bash
# Open the PostgreSQL shell
psql -U postgres

# Inside psql:
CREATE DATABASE sokocater;
CREATE USER sokocater_user WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE sokocater TO sokocater_user;
\q
```

> On PostgreSQL 15+, you may also need to run `GRANT ALL ON SCHEMA public TO sokocater_user;` while connected to the `sokocater` database.

### 3. Backend setup

```bash
cd backend

# Install dependencies and activate the virtual environment
pipenv install
pipenv shell

# Create your .env file (see Environment Variables below)
cp .env.example .env

# Run migrations to create the tables
flask db init          # first time only
flask db migrate -m "initial migration"
flask db upgrade

# Seed sample data, including the admin account
python seed.py

# Run the server
flask run
```

The API will be available at `http://localhost:5000`. Confirm it's running by visiting `http://localhost:5000/api/health`.

### 4. Frontend setup

```bash
cd frontend
npm install
npm start
```

The app will be available at `http://localhost:3000`.

### 5. Try the access levels

After seeding, log in with the demo accounts to see each role's view:

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@sokocater.com` | *(set in seed.py)* |
| Caterer | `caterer@sokocater.com` | *(set in seed.py)* |
| Customer | `customer@sokocater.com` | *(set in seed.py)* |

> ✏️ **Team:** update these once `seed.py` is written, and never use real passwords here.

---

## 🔐 Environment Variables

Create a `.env` file in the `backend/` directory:

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_EXPIRES_HOURS=1
DATABASE_URL=postgresql://sokocater_user:your-password@localhost:5432/sokocater
CORS_ORIGINS=http://localhost:3000
```

> ⚠️ Never commit your `.env` file. Commit a `.env.example` with placeholder values instead.

---

## 📡 API Reference

> ✏️ **Team: adjust routes to match the final implementation.**
>
> 🔑 = requires a valid JWT. The **Access** column shows which roles may call the endpoint.

### Health Check

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| `GET` | `/api/health` | Public | Confirms the API is running (returns `200 OK`) |

```json
{ "status": "ok" }
```

### Authentication

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| `POST` | `/api/signup` | Public | Register as a customer or caterer |
| `POST` | `/api/login` | Public | Log in and receive a JWT |
| `GET` | `/api/me` 🔑 | Any logged-in user | Get the current user and role |
| `DELETE` | `/api/logout` 🔑 | Any logged-in user | Log out |

### Caterers

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| `GET` | `/api/caterers` | Public | List caterers (supports filters) |
| `GET` | `/api/caterers/:id` | Public | Get a caterer's details |
| `POST` | `/api/caterers` 🔑 | Caterer | Create a caterer profile |
| `PATCH` | `/api/caterers/:id` 🔑 | Owner caterer, Admin | Update a caterer profile |

### Menu Items

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| `GET` | `/api/caterers/:id/menus` | Public | List a caterer's menu items |
| `POST` | `/api/menus` 🔑 | Caterer | Add a menu item |
| `PATCH` | `/api/menus/:id` 🔑 | Owner caterer, Admin | Update a menu item |
| `DELETE` | `/api/menus/:id` 🔑 | Owner caterer, Admin | Remove a menu item |

### Bookings

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| `GET` | `/api/bookings` 🔑 | Customer (own), Caterer (received), Admin (all) | List bookings |
| `POST` | `/api/bookings` 🔑 | Customer | Create a booking request |
| `PATCH` | `/api/bookings/:id` 🔑 | Customer (cancel own), Caterer (accept/decline), Admin | Update booking status |

### Reviews

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| `GET` | `/api/caterers/:id/reviews` | Public | List reviews for a caterer |
| `POST` | `/api/reviews` 🔑 | Customer | Review a completed booking |
| `DELETE` | `/api/reviews/:id` 🔑 | Admin | Remove an inappropriate review |

### Admin

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| `GET` | `/api/admin/users` 🔑 | Admin | List all users |
| `PATCH` | `/api/admin/users/:id/role` 🔑 | Admin | Change a user's role |
| `PATCH` | `/api/admin/caterers/:id/verify` 🔑 | Admin | Verify a caterer |

### Error responses

| Status | Meaning |
|--------|---------|
| `401 Unauthorized` | Missing, invalid, or expired token |
| `403 Forbidden` | Logged in, but your role isn't allowed to do this |
| `404 Not Found` | Resource doesn't exist |
| `422 Unprocessable Entity` | Validation failed (bad or missing fields) |

**Example: log in**

```http
POST /api/login
Content-Type: application/json

{
  "email": "customer@sokocater.com",
  "password": "your-password"
}
```

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": { "id": 5, "full_name": "Jane Wanjiku", "role": "customer" }
}
```

**Example: create a booking (customer only)**

```http
POST /api/bookings
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "caterer_id": 3,
  "event_date": "2026-12-20",
  "event_type": "Wedding",
  "guest_count": 150,
  "notes": "Vegetarian options needed"
}
```

```json
{
  "id": 12,
  "caterer_id": 3,
  "status": "pending",
  "event_date": "2026-12-20",
  "guest_count": 150
}
```

---

## 📂 Project Structure

```
tpka-sokocater-platform/
├── frontend/                  # React app
│   ├── public/
│   └── src/
│       ├── components/        # Reusable UI (Navbar, ProtectedRoute, ...)
│       ├── pages/             # Home, Login, Caterers, Dashboards (per role)
│       ├── context/           # Auth context (current user + role)
│       └── App.js
├── backend/                   # Flask API
│   ├── app.py
│   ├── config.py
│   ├── models.py
│   ├── decorators.py          # role_required and ownership checks
│   ├── routes/                # auth, caterers, menus, bookings, reviews, admin
│   ├── seed.py
│   └── migrations/
├── docs/                      # ERD, database design, wireframes
├── .github/
│   └── pull_request_template.md
├── .env.example
├── .gitignore
└── README.md
```

---

## 🧪 Testing

```bash
# Backend
cd backend
pytest -v

# Frontend
cd frontend
npm test
```

**Access-control cases to cover:**
- A customer calling a caterer-only route gets `403`.
- A request without a token gets `401`.
- A caterer can't edit another caterer's menu.
- Public signup can't create an `admin`.

---

## 👥 Team & Workflow

SokoCater Platform is built by a team of four following **Agile / Scrum**.

| Name | Role | GitHub |
|------|------|--------|
| **Talise** | Scrum Master, README & Documentation | [@username](https://github.com/username) |
| **Praise** | Backend Developer (Flask API) | [@username](https://github.com/username) |
| **Kate** | Database Schema & Design | [@username](https://github.com/username) |
| **Allan** | UI/UX Wireframes & Frontend Developer (React) | [@username](https://github.com/username) |

**Workflow**
- Work is tracked as GitHub Issues on a GitHub Projects board (To Do / In Progress / Done) and organized into sprints.
- Each task gets its own branch, e.g. `feature/<short-description>` or `docs/<short-description>`.
- Changes land on `main` through pull requests, and teammates review each other's work before merging.
- Daily stand-ups and sprint reviews/retrospectives keep the team aligned.

**Commit convention**

```
feat: add booking creation endpoint
fix: correct availability check on weekends
docs: update README setup steps
```

---

## 🗺️ Roadmap

### Sprint 1: Blueprint & Foundation (Days 1 to 2)

**Goal:** environment setup, database schema design, boilerplate initialization, and wireframes.

| Area | Owner | Deliverables |
|------|-------|--------------|
| **Backend (Flask)** | Praise | App structure, virtual environment, SQLAlchemy models, database connection (SQLite or PostgreSQL), working `/api/health` endpoint |
| **Database** | Kate | Schema design and ERD (see [`docs/database-design.md`](docs/database-design.md)) |
| **Frontend (React)** | Allan | Wireframes and design in a tool of the team's choice (link below), React boilerplate |
| **Agile artifacts** | Talise (Scrum Master) | GitHub repository, project board (GitHub Projects) with the initial backlog, README and documentation |

**Wireframes:** *(add the Figma / design tool link here)*

📄 Full sprint details, backlog and retrospective: [`docs/sprint-1.md`](docs/sprint-1.md)

#### ✅ Milestone Gate 1 (end of Day 2)

- [ ] Working local development environments for every team member
- [ ] `main` branch merged with the initial boilerplate
- [ ] Approved schema diagram (ERD)
- [ ] `/api/health` endpoint returns `200 OK`
- [ ] GitHub repository and project board created, with the initial backlog

### Planned Features (later sprints)

- [x] Problem statement, user stories, and ERD
- [ ] Authentication (signup, login, JWT)
- [ ] Role-based access control (customer, caterer, admin)
- [ ] Caterer profiles, menus, and packages
- [ ] Search and filtering
- [ ] Booking flow and status management
- [ ] Reviews and ratings
- [ ] Admin dashboard (verify caterers, manage users)
- [ ] Payment integration (e.g. M-Pesa)
- [ ] Email / SMS notifications
- [ ] Deployment

---

## 🤝 Contributing

1. Clone the repository
2. Create a branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "feat: your feature"`
4. Push to your branch: `git push origin feature/your-feature`
5. Open a Pull Request using the template and request a review

---

## 📄 License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.

---

<div align="center">

Made with ❤️ by the SokoCater Platform team

</div>