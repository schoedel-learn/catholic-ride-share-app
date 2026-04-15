# About Catholic Ride Share

← [Home](Home)

## Mission

> *To strengthen Catholic communities by ensuring that transportation is never a barrier to participating in the sacraments and church life.*

Catholic Ride Share is a community-driven, volunteer-based ride-sharing application that connects Catholics who need transportation to Mass, Confession, prayer events, and church social functions with volunteer drivers who are willing to help – with a special focus on rural areas where distances can be long and public transit is unavailable.

---

## Core Principles

| Principle | Description |
|-----------|-------------|
| **Volunteer-based** | Rides are provided by willing community members, not paid contractors. |
| **No required payment** | Riders are never charged. An optional post-ride donation to the driver is the only monetary feature. |
| **Rural-friendly** | There is no hard distance limit. Distance is shown as information to help riders and drivers decide; it never acts as a barrier. |
| **Privacy-first** | Only the data needed to coordinate a ride is stored. Pickup and destination locations are blurred until a ride is accepted. |
| **Admin-supported** | Administrators verify drivers, monitor the platform, and resolve issues to maintain community trust and safety. |

---

## How It Works

1. **Rider** creates an account, verifies their email, and submits a ride request with a pickup location, destination, and optional parish reference.
2. **Driver** (a verified volunteer) sees ride requests in their area and chooses which rides they are willing to take.
3. Once a driver accepts a ride, precise location details are shared between the two parties.
4. After the ride, the rider can optionally leave a rating and make a donation to the driver through Stripe.

---

## Feature Status

### Implemented (backend foundation)

- **Authentication & accounts**
  - User registration with email and password
  - JWT-based login (access token + refresh token)
  - Email verification with 6-digit codes (required before ride features)
  - Secure, single-use password reset flow

- **User profiles**
  - Rider / driver / both / admin roles
  - Basic profile data (name, phone, parish reference)
  - Optional profile photo upload (stored on AWS S3, resized to 500×500)

- **Core data models**
  - `User` with optional last-known geospatial location
  - `DriverProfile` for vehicle and driver status
  - `Parish` – name + postal address only (no Mass times or URLs)
  - `RideRequest` and `Ride` models

- **Infrastructure**
  - Dockerized stack: FastAPI backend, PostgreSQL + PostGIS, Redis, Celery worker
  - Alembic database migrations

### In Active Development

- Complete driver profile management (vehicle details, documents)
- Multi-step driver verification (background checks, safe environment training, admin approval)
- Driver availability scheduling
- Ride request creation, matching, and lifecycle management
- In-ride messaging (WebSocket / Socket.IO)
- Push notifications (Firebase Cloud Messaging) + email notifications
- Post-ride ratings and optional Stripe donations
- Admin dashboard for verifications and statistics

### Planned (Future)

- Flutter mobile app (primary client for riders and drivers)
- AI-powered ride matching suggestions
- AI assistant for parish and ride questions
- Multi-language support

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend framework | FastAPI (Python 3.11+) |
| Database | PostgreSQL with PostGIS (geospatial) |
| Cache | Redis |
| Task queue | Celery |
| Authentication | JWT with OAuth2 |
| File storage | AWS S3 |
| Payments | Stripe (optional donations only) |
| Background checks | Checkr (planned) |
| Push notifications | Firebase Cloud Messaging (planned) |
| AI/ML | OpenAI / Anthropic APIs, scikit-learn (planned) |
| Mobile client | Flutter (planned) |
| Web frontend | Next.js + Tailwind (scaffold/admin) |
| Infrastructure | Docker & Docker Compose |

---

## API Overview

All endpoints are versioned under `/api/v1`. See the [README](https://github.com/schoedel-learn/catholic-ride-share-app/blob/main/README.md) or the live Swagger docs at `http://localhost:8000/docs` for a full reference.

### Authentication

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/auth/register` | Register a new user |
| `POST /api/v1/auth/login` | Login and receive tokens |
| `POST /api/v1/auth/verify-email` | Verify email with 6-digit code |
| `POST /api/v1/auth/forgot-password` | Initiate password reset |
| `POST /api/v1/auth/reset-password` | Complete password reset |

### Users

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/users/me` | Get current user profile |
| `PUT /api/v1/users/me` | Update current user profile |
| `POST /api/v1/users/me/photo` | Upload profile photo |
| `DELETE /api/v1/users/me/photo` | Remove profile photo |

### Rides, Drivers, Parishes *(partially stubbed – in development)*

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/rides/` | Create a ride request |
| `GET /api/v1/rides/` | List rides for current user |
| `POST /api/v1/drivers/profile` | Create/update driver profile |
| `GET /api/v1/drivers/available` | Discover available drivers nearby |
| `GET /api/v1/parishes/` | List parishes (name + address) |

---

## Security

- Passwords hashed with bcrypt via passlib
- JWT tokens with expiration and secure refresh
- All inputs validated by Pydantic schemas
- SQLAlchemy ORM prevents SQL injection
- Rate limiting on authentication endpoints
- CodeQL scanning, secret scanning, and Dependabot in CI
- Location data blurred until a ride is accepted

---

## Getting Started

See the main [README](https://github.com/schoedel-learn/catholic-ride-share-app/blob/main/README.md) for full setup instructions. Quick-start summary:

```bash
# Copy env files
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local

# Start the full stack
docker compose up --build

# Seed demo data
docker compose run --rm backend python app/seed_demo.py
```

Demo accounts:
- **Rider**: `rider.demo@example.com` / `Password123!`
- **Driver**: `driver.demo@example.com` / `Password123!`

---

## Contributing

Catholic Ride Share is an open-source, community project. See [CONTRIBUTING.md](https://github.com/schoedel-learn/catholic-ride-share-app/blob/main/CONTRIBUTING.md) for guidelines. The `main` branch is protected and requires passing CI and a pull request review before merging.
