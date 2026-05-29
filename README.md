# Job Portal — Backend

A REST + WebSocket API for a task marketplace (Airtasker-style) where customers post jobs and taskers bid, chat, complete work, and get paid through an escrow-backed wallet. Built with **Django 5** and **Django REST Framework**, with real-time chat, background jobs, and localized payments for Nepal (Khalti / eSewa).

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 5, Django REST Framework |
| Auth | SimpleJWT, django-allauth (Google / Facebook OAuth) |
| Real-time | Django Channels, Daphne, Redis |
| Background jobs | Celery, Celery Beat, django-celery-results |
| Database | PostgreSQL (SQLite for local dev) |
| Cache / Broker | Redis |
| Payments | Khalti, eSewa, wallet escrow |
| Storage | Local / AWS S3 / Cloudinary |
| API docs | drf-spectacular (OpenAPI) |
| Admin | Jazzmin + custom analytics dashboards |

---

## Features

- **Authentication** — email + JWT, social login (Google/Facebook), phone/SMS verification.
- **Tasks & Bids** — post tasks, browse, bid, accept, and track a full task lifecycle/workflow.
- **Wallet & Escrow** — recharges, withdrawals, fees, and automatic escrow release after a customer approval window.
- **Payments** — Khalti and eSewa gateways (Nepal) plus manual wallet recharge flow.
- **Real-time Chat** — WebSocket messaging between customers and taskers.
- **Reviews & Badges** — ratings and verified tasker badges.
- **Disputes & Rules** — a configurable rule engine handling refunds, cancellations, and dispute resolution.
- **Notifications** — in-app and email notifications.
- **Admin Analytics** — premium dashboards for business metrics, payments, tasks, and users.

---

## Project Structure

```
backend/
├── apps/
│   ├── users/          # Accounts, profiles, roles, badges
│   ├── accounts/       # Auth & social login
│   ├── tasks/          # Task posting & lifecycle
│   ├── bids/           # Bidding & workflow
│   ├── wallets/        # Wallet, recharge, withdrawals
│   ├── payments/       # Khalti / eSewa / escrow
│   ├── fees/           # Platform fee config
│   ├── chat/           # Real-time messaging (Channels)
│   ├── reviews/        # Ratings & reviews
│   ├── disputes/       # Dispute handling
│   ├── rules/          # Refund / cancellation rule engine
│   ├── notifications/  # In-app & email notifications
│   ├── analytics/      # Business metrics & dashboards
│   ├── locations/      # Countries, cities, service areas
│   ├── search/         # Task / tasker search
│   ├── dashboard/      # Shared admin dashboard utils
│   ├── blog/           # Blog content
│   └── uploads/        # File uploads
├── config/             # Settings, URLs, ASGI/WSGI
├── requirements/       # Dependency files
├── templates/          # Admin & email templates
├── utils/              # Shared helpers & middleware
└── manage.py
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis 6+

### Setup

```bash
# 1. Clone & enter
git clone https://github.com/everpeaknp/Job-Portal-Backend.git
cd Job-Portal-Backend

# 2. Virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Dependencies
pip install -r requirements/base.txt

# 4. Environment
cp .env.example .env            # then fill in the values

# 5. Database
python manage.py migrate
python manage.py createsuperuser

# 6. Run
python manage.py runserver
```

### Background services

```bash
# Celery worker
celery -A config worker -l info

# Celery beat (scheduled tasks)
celery -A config beat -l info
```

> For WebSocket/real-time features, run the app with Daphne (ASGI): `daphne config.asgi:application`.

---

## Environment Variables

Copy `.env.example` to `.env` and configure. Key groups:

- **Django** — `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DJANGO_SETTINGS_MODULE`
- **Database / Cache** — `DATABASE_URL`, `REDIS_URL`, `CELERY_BROKER_URL`
- **Auth** — `JWT_*`, `GOOGLE_*`, `FACEBOOK_*`
- **Payments** — `KHALTI_*`, `ESEWA_*`, `ESCROW_AUTO_RELEASE_HOURS`
- **Notifications** — `EMAIL_*`, `TWILIO_*`, `SMS_GATEWAY_*`

See `.env.example` for the full list.

---

## API Documentation

With the server running:

- OpenAPI schema: `/api/schema/`
- Swagger UI: `/api/schema/swagger-ui/`
- Admin: `/admin/`

---

## License

Proprietary — All rights reserved.
