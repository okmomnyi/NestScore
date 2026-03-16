# NestScore

"Know your plot before you sign." — A peer-to-peer student housing rating and discovery platform dedicated to students at Meru University of Science and Technology (MUST).

NestScore focuses on providing transparent, anonymous, and authentic reviews of student hostels and apartments in the areas surrounding MUST, including **Nchiru, Kianjai, Mascan, and Kunene**.

## Features

-   **Student Housing Discovery:** Browse real student hostels near Meru University with accurate GPS locations and weighted quality scores.
-   **Anonymous Review System:** Share your experience without fear. Reviews use automatically generated random nicknames (e.g., *SwiftStudent803*) to protect your identity.
-   **Instant Feedback:** Reviews appear immediately after submission, allowing for real-time community insights.
-   **Landlord Engagement:** Verified landlord responses to address student concerns directly.
-   **"No" Service Security:** Enhanced security and error handling that provides clear, humorous, yet strict rejection for unauthorized access or invalid requests.
-   **Anomaly Detection:** Built-in safeguards against review bombing and fraudulent ratings using IP and browser fingerprinting.
-   **AI-Free Architecture:** Lean, fast, and cost-effective system running on a modern Python/React stack without expensive AI dependencies.

## Tech Stack

-   **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.13), [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (Async), [PostgreSQL](https://neon.tech/) (Serverless), [Redis](https://redis.io/) (Caching & Rate Limiting).
-   **Frontend:** [Next.js 14](https://nextjs.org/) (App Router), [React](https://react.dev/), [Tailwind CSS](https://tailwindcss.com/), [Lucide React](https://lucide.dev/).
-   **Security:** [SlowAPI](https://github.com/laurentS/slowapi) for rate limiting, [Bleach](https://github.com/mozilla/bleach) for HTML sanitization, and custom IP/Fingerprint hashing.
-   **Infrastructure:** Docker, Docker Compose, Nginx.

## Setup Instructions

### 1. Environment Configuration

Copy the example environment file and fill in your secrets:

```bash
cp .env.example .env
```

Ensure you have a working **Neon Postgres** connection string and a **Redis** instance.

### 2. Backend Setup

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Unix: source venv/bin/activate

pip install -r requirements.txt

# Create/Update database tables
python create_tables.py

# Populate with Meru student housing data
python scripts/populate_meru_data.py
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 4. Direct Docker Start

If you prefer using Docker:

```bash
docker-compose up --build
```

Access the app at `http://localhost:3000`.

## Directory Structure

-   `/backend`: FastAPI application, models, and background services.
-   `/frontend`: Next.js application and UI components.
-   `/scripts`: Database population and maintenance utilities.
-   `/alembic`: Database migration configuration.

## Admin Access

The admin panel is accessible at `/manage` (configurable via `ADMIN_PATH`) and is protected by:
- **IP Allowlist:** Add your IP to `ADMIN_IP_ALLOWLIST` in `.env`
- **Password Authentication:** Default password is `admin123` (bcrypt hashed)
- **Session Cookies:** 8-hour encrypted sessions

### Admin Features
- Dashboard with real-time statistics
- Review moderation (approve/remove/clear flags)
- Plot management (create/update/remove)
- Dispute resolution
- Plot suggestion approval
- Audit log tracking
- Bulk score recalculation

### Changing Admin Password

```bash
cd backend
python -c "import bcrypt; print(bcrypt.hashpw(b'your-new-password', bcrypt.gensalt()).decode())"
```

Copy the output and update `ADMIN_PASSWORD_HASH` in `.env`.

## Google Analytics Setup

1. Create a Google Analytics 4 property at [analytics.google.com](https://analytics.google.com)
2. Get your Measurement ID (format: `G-XXXXXXXXXX`)
3. Update `.env` files:
   - Backend: `NEXT_PUBLIC_GA_MEASUREMENT_ID=G-XXXXXXXXXX`
   - Admin panel: Update `G-XXXXXXXXXX` in `backend/app/admin_ui/templates/base.html`

### Tracked Events
- Page views (automatic)
- Review submissions
- Plot views
- Search queries
- Dispute submissions
- Suggestion submissions
- Contact form submissions
- Map interactions
- Filter changes

---
© 2026 NestScore Community.
