# Catholic Ride Share

[![Tests](https://github.com/schoedel-learn/catholic-ride-share-app/actions/workflows/test.yml/badge.svg)](https://github.com/schoedel-learn/catholic-ride-share-app/actions/workflows/test.yml)
[![CodeQL](https://github.com/schoedel-learn/catholic-ride-share-app/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/schoedel-learn/catholic-ride-share-app/actions/workflows/codeql-analysis.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

> **🚀 Use this template** — Click the green **"Use this template"** button at the top of this page to create your own copy of this project and adapt it for your community or diocese.

A community-driven ride-sharing application connecting Catholics who need transportation to Mass, Confession, prayer events, and church social functions with volunteer drivers who are willing to help – especially in rural areas where distances can be long.

## Mission

To strengthen Catholic communities by ensuring that transportation is never a barrier to participating in the sacraments and church life.

> **📋 For Stakeholders**: If you're evaluating this project and have questions about risk, liability, or security, please see our comprehensive [Stakeholder Guide](docs/STAKEHOLDER_GUIDE.md) which addresses these concerns in detail.

## Open Source & Self-Hosted by Communities

Catholic Ride Share is an open-source project intended for **installation, operation, and customization by parishes, dioceses, and Catholic organizations**.

- You can run your own instance for your local community.
- You can customize workflows, policies, and integrations for local needs and diocesan requirements.
- You can contribute improvements back to the shared open-source codebase.

The core maintainers currently steward the repository and may offer managed hosting in the future, but **self-hosting and community ownership are first-class goals today**.

## 💬 Community & Discussions

We'd love to hear from you! Whether you're a developer, a parish coordinator, a driver, a rider, or just someone who cares about this mission — you're welcome here.

- **[Start or join a Discussion](https://github.com/schoedel-learn/catholic-ride-share-app/discussions)** — ask questions, share ideas, introduce yourself, or talk about anything related to the project.
- **[Browse open Issues](https://github.com/schoedel-learn/catholic-ride-share-app/issues)** — see what's being worked on and where you can help.
- **[Read CONTRIBUTING.md](CONTRIBUTING.md)** — learn how to contribute code, docs, or testing.
- **[Code of Conduct](CODE_OF_CONDUCT.md)** — we follow a charitable, welcoming standard for all interactions.

> 💡 **Not a developer?** Discussions are the best place for you. You can share your perspective on features, report problems you've experienced, or simply encourage the team — all you need is a free GitHub account.

## What We Are Building

At a high level, Catholic Ride Share is:

- A **volunteer ride network**: riders request help getting to church activities; drivers choose which rides they are willing to take.
- **Rural-friendly**: rides may be 10, 20, or more miles away; there is **no hard distance limit**. Distance is information, not a gate.
- **Privacy-conscious**: only the information needed to coordinate rides is stored; parish records only include **full name and address**, not Mass times or links that change frequently.
- **Donation-based**: riders can optionally offer donations after rides (via Stripe); there is no required payment for rides.
- **Admin-supported**: admins can verify drivers, monitor the system, and help resolve issues.
- **Deployable by your community**: each parish/diocese can operate its own instance with local governance and policies.

## Feature Overview

### Implemented

- **Authentication & accounts**
  - User registration with email and password.
  - JWT-based login (`access_token` + `refresh_token`).
  - Email verification with 6-digit codes (required before using ride features).
  - Password reset flow with secure, single-use reset tokens.
- **User profiles**
  - Rider/driver/both/admin/coordinator roles.
  - Basic profile data (name, phone, parish reference).
  - Optional profile photo upload (stored on S3, resized to 500x500 thumbnail).
  - Location update (`PUT /users/me/location`).
- **Driver experience**
  - `POST /drivers/profile` — idempotent upsert of vehicle details (make, model, year, color, plate, capacity).
  - `PUT /drivers/me` — update an existing profile.
  - `PUT /drivers/me/availability` — toggle driver availability.
  - `GET /drivers/me/verification-status` — human-friendly verification summary.
  - `GET /drivers/available` — list approved, available drivers; PostGIS distance ordering when coordinates are provided.
  - Frontend driver profile setup page (`/driver-profile`) with verification status banner.
- **Rider experience**
  - `POST /rides/` — create a ride request with pickup/dropoff locations.
  - `POST /rides/{id}/accept` — driver accepts a request (creates a `Ride`).
  - `PATCH /rides/{id}/status` — driver updates status through enforced state machine.
  - `POST /rides/{id}/cancel` — rider cancels a pending or accepted request.
  - Real-time WebSocket push on status changes and new requests.
  - Dashboard Cancel button for pending/accepted ride requests.
- **Ride-scoped messaging**
  - `POST /rides/{id}/messages` — send a chat message within an active ride.
  - `GET /rides/{id}/messages` — retrieve the message thread.
  - Authorization: only the rider, assigned driver, and admins may read/write.
- **Donations & reviews**
  - Post-ride star rating and optional Stripe donation.
  - Donation preferences (fixed or distance-based auto-donation).
- **Admin tools**
  - `GET /admin/drivers` — list all drivers (admin) or parish-scoped drivers (coordinator).
  - `PUT /admin/drivers/{id}/verify` — update training dates and background check status.
  - `POST /admin/drivers/{id}/approve` — one-click approve (admin only).
  - `POST /admin/drivers/{id}/reject` — one-click reject with optional reason (admin only).
  - `GET /admin/parish/stats` — summary statistics.
  - Next.js admin page with Approve/Reject quick-action buttons.
- **Infrastructure**
  - Dockerized stack: FastAPI backend, Postgres + PostGIS, Redis, Celery worker.
  - Alembic migrations (9 versions through ride messages table).
  - Celery task stubs for ride and verification notifications (`app/tasks/notifications.py`).
  - 28 pytest tests covering auth, rides, drivers, admin, and lifecycle edge cases.

### Planned / In Progress

- **Driver document uploads** — license, insurance, and Safe Environment Training proof.
- **Push notifications** — FCM/APNS integration for ride acceptance, status changes, and verification updates (Celery stubs are in place; delivery mechanism TBD).
- **Address/map-based ride creation** — replace manual lat/lng entry in the dashboard.
- **Parish admin CRUD** — create, update, import, and geocode parishes from the admin UI.
- **Flutter mobile client** — primary rider/driver experience (see `braingrid-improvements`).
- **AI & assistance (future)** — AI-powered matching suggestions and multilingual support.

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with PostGIS (geospatial)
- **Cache**: Redis
- **Task Queue**: Celery
- **Authentication**: JWT with OAuth2

### AI/ML
- OpenAI/Anthropic APIs for chatbot
- scikit-learn for matching algorithms
- Google Maps API for routing

### Infrastructure
- Docker & Docker Compose
- PostgreSQL with PostGIS extension
- Redis for caching and pub/sub

### Frontend / Clients

- **Current**: Backend-first plus a starter Next.js + Tailwind web scaffold in `frontend/` (accessibility-focused, not production-ready).
- **Planned**:
  - Flutter mobile app (primary client) for riders and drivers.
  - Lightweight web/admin frontend for admins and operations.

## Project Structure

```
catholic-ride-share/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/      # API route handlers
│   │   │   └── deps/           # Dependencies (auth, etc.)
│   │   ├── core/               # Config and security
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/           # Business logic
│   │   ├── ai/                 # AI/ML services
│   │   ├── db/                 # Database session
│   │   └── utils/              # Utilities
│   ├── tests/                  # Test suite
│   ├── alembic/                # Database migrations
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile
├── frontend/                   # Future: React Native or React
├── docs/                       # Documentation
├── docker-compose.yml
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL (if not using Docker)
- Redis (if not using Docker)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/catholic-ride-share.git
   cd catholic-ride-share
   ```

2. **Set up environment variables**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your configuration
   ```
   > **Important:** Set strong, unique values for `POSTGRES_PASSWORD` (used by `docker-compose.prod.yml`) and `SECRET_KEY`. The example file now ships with placeholders only, so deployments will fail until you provide real credentials.

3. **Using Docker (Recommended)**
   ```bash
   # Start all services
   docker-compose up -d

   # Run database migrations
   docker-compose exec backend alembic upgrade head

   # View logs
   docker-compose logs -f backend
   ```

4. **Manual Setup (Alternative)**
   ```bash
   # Create virtual environment
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Run migrations
   alembic upgrade head

   # Start the application
   uvicorn app.main:app --reload
   ```

### Accessing the Application

- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Frontend (Next.js + Tailwind) Preview

```bash
cd frontend
npm install
npm run dev
```
The scaffold uses the App Router, Tailwind, and accessibility-minded defaults to prototype the web/admin experience.

## Development

### Running Tests
```bash
cd backend
pytest
```

### Frontend Lint
```bash
cd frontend
npm run lint
```

### Code Quality
```bash
# Format code
black .

# Sort imports
isort .

# Lint
flake8 .

# Type checking
mypy .
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## API Endpoints

The backend is versioned under `/api/v1`. Some endpoints are fully implemented; others are present as stubs and will be expanded.

### Authentication (implemented)

- `POST /api/v1/auth/register`  
  Register a new user (creates an account and sends a verification email).

- `POST /api/v1/auth/login`  
  Login with email + password and receive access/refresh tokens.

- `POST /api/v1/auth/verify-email`  
  Verify email using a 6‑digit code sent to the user’s email.

- `POST /api/v1/auth/resend-verification`  
  Request that a new verification email be sent (idempotent-style behavior).

- `POST /api/v1/auth/forgot-password`  
  Initiate a password reset; always returns a generic success message and is rate-limited to prevent abuse and email enumeration.

- `POST /api/v1/auth/validate-reset-token`  
  Check whether a reset token is still valid.

- `POST /api/v1/auth/reset-password`  
  Reset a user’s password using a valid, single-use reset token.

### Users (implemented)

- `GET /api/v1/users/me`  
  Get the currently authenticated user’s profile.

- `PUT /api/v1/users/me`  
  Update the current user’s profile (name, phone, parish reference, etc.).

- `POST /api/v1/users/me/photo`  
  Upload or replace the current user’s profile photo (JPEG/PNG/WebP ≤ 5MB, stored in S3 as a 500×500 thumbnail).

- `DELETE /api/v1/users/me/photo`  
  Remove the current user’s profile photo (deletes the S3 object on a best-effort basis).

- `GET /api/v1/users/{user_id}`  
  Get another user’s public profile by ID (requires authentication).

### Rides, Drivers, Parishes (planned / partially stubbed)

These routes exist as placeholders and will be built out according to the strategic plan:

- `POST /api/v1/rides/` – Create ride request (planned: full request schema and matching).  
- `GET /api/v1/rides/` – List rides for the current user (planned).  
- `POST /api/v1/drivers/profile` – Create/update driver profile (planned).  
- `GET /api/v1/drivers/available` – Discover available/willing drivers nearby (planned; **no fixed distance limit**, distance used for ordering only).  
- `GET /api/v1/parishes/` – List parishes (full name + address only).  
- `GET /api/v1/parishes/{id}` – Get parish details (full name + address only).

## Environment Variables

Key environment variables (see `.env.example` for complete list):

- `SECRET_KEY` - JWT secret key (CHANGE IN PRODUCTION)
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `GOOGLE_MAPS_API_KEY` - For routing and geocoding (future features)

Email / notifications:
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` - Outbound email configuration
- `EMAILS_FROM_EMAIL`, `EMAILS_FROM_NAME` - From-address details

Storage:
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` - AWS credentials
- `AWS_S3_BUCKET` - S3 bucket for profile photos and documents
- `AWS_REGION` - AWS region for the bucket

Payments:
- `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET` - For donation processing (optional)

Background checks / notifications (future):
- `CHECKR_API_KEY` - For background check integration (optional)
- `FIREBASE_CREDENTIALS_PATH`, `FIREBASE_PROJECT_ID` - For Firebase Cloud Messaging

AI (future):
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` - For AI assistant and matching features

## Demo Quickstart

1) Copy env files:
   - `cp backend/.env.example backend/.env`
   - `cp frontend/.env.local.example frontend/.env.local`
   - Update `SECRET_KEY` and any SMTP credentials if you plan to send real email.
2) Start the stack: `docker compose up --build`
3) Seed demo data (rider, driver, parishes, sample rides):  
   `docker compose run --rm backend python app/seed_demo.py`
4) Frontend: http://localhost:3000  
   Backend API docs: http://localhost:8000/docs
5) Demo accounts:  
   - Rider: `rider.demo@example.com` / `Password123!`  
   - Driver: `driver.demo@example.com` / `Password123!`

Notes:
- If SMTP is not configured, verification and reset codes are logged to the backend console for local demos.
- Redis/Postgres addresses in `.env` are pre-set for docker-compose (`db`, `redis`).

## Contributing

This is a community project. Contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

**Note**: The `main` branch is protected and requires pull request reviews and passing CI tests before merging. See [Branch Protection Documentation](docs/BRANCH_PROTECTION.md) for details.

## External Integrations

If you're using external tools like BrainGrid, GitHub Copilot, or other integrations with this repository, please see the [External Integrations Guide](docs/EXTERNAL_INTEGRATIONS.md) for setup instructions and troubleshooting.

## Security

Catholic Ride Share takes security seriously. We use multiple layers of protection:

- **GitHub Advanced Security**: CodeQL scanning, secret scanning, and dependency scanning
- **Automated Updates**: Dependabot monitors and updates vulnerable dependencies
- **Authentication**: JWT tokens with expiration and secure refresh mechanism
- **Password Security**: Bcrypt hashing with proper salt
- **Input Validation**: Pydantic schemas validate all user inputs
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries
- **Environment Security**: Never commit `.env` files or credentials
- **CORS Configuration**: Controlled cross-origin resource sharing

For security vulnerabilities, see [SECURITY.md](SECURITY.md) for responsible disclosure.

For setting up GitHub security features, see [GitHub Security Setup Guide](docs/GITHUB_SECURITY_SETUP.md).

## License

This project is licensed under the [MIT License](LICENSE). Built with love to serve the Catholic community.

## Roadmap

The detailed technical roadmap is maintained in the `braingrid-improvements` document and implemented in phases. In summary:

- **Foundation**: Core backend, authentication, email verification, password reset, and profile photos.  
- **Drivers & availability**: Driver profiles, verification, and availability (scheduled + “available now”).  
- **Rides & lifecycle**: Ride requests, matching based on willing drivers (not strict radius), ride status transitions, and cancellation rules.  
- **Messaging & notifications**: In-app messaging, push notifications, and email alerts.  
- **Donations & reviews**: Post-ride ratings and optional donations via Stripe.  
- **Parishes**: Simple parish records (name + address only) with geospatial search.  
- **Admin & analytics**: Admin APIs and dashboards for verification, issues, and high-level stats.  
- **Clients & AI**: Flutter mobile app, admin web UI, and AI-assisted matching/assistant.

## Documentation

- **[Stakeholder Guide](docs/STAKEHOLDER_GUIDE.md)** - Comprehensive information on risk, liability, security, and safety for stakeholders
- **[Architecture](docs/ARCHITECTURE.md)** - Technical architecture and system design
- **[Deployment Guide](docs/DEPLOYMENT.md)** - How to set up GitHub Actions secrets and production environment secrets on the VPS
- **[Contributing](CONTRIBUTING.md)** - How to contribute to the project
- **[Code of Conduct](CODE_OF_CONDUCT.md)** - Community standards for respectful interaction

## Support

For questions or support, please open an issue on GitHub.

## Acknowledgments

Built with love for the Catholic community to ensure everyone can participate in the life of the Church.
