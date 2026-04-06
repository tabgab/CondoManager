# CondoManager - System Architecture

## Overview
CondoManager is a multi-role communication and task management system for condominium buildings. It connects Apartment Owners/Tenants, Employees (caretakers, cleaners, maintenance), and Condo Managers in a unified platform.

---

## Technology Stack

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **UI Library**: Tailwind CSS + shadcn/ui (accessible, clean components)
- **State Management**: Zustand + React Query (TanStack Query)
- **PWA**: Vite PWA plugin → installable on Android, iPhone, Windows, macOS
- **Real-time**: WebSocket (native browser API)
- **Routing**: React Router v6
- **Forms**: React Hook Form + Zod validation
- **File Uploads**: Dropzone.js

### Backend
- **Framework**: Python FastAPI (async, OpenAPI auto-docs, lightweight)
- **ORM**: SQLAlchemy 2.0 (async) + Alembic migrations
- **Auth**: JWT (python-jose) + bcrypt password hashing
- **WebSockets**: FastAPI WebSocket support
- **Task Queue**: APScheduler (recurring tasks, no Redis needed for free tier)
- **Email**: SendGrid API (free tier: 100 emails/day) or Resend (3,000/month free)
- **Fallback**: Gmail App Password (requires 2FA enabled on account)
- **Telegram Bot**: python-telegram-bot v20 (async)
- **WhatsApp**: Meta Cloud API (free, no charge for messages)
- **File Storage**: Cloudinary free tier (10GB, 25K transforms/month)

### Database
- **Production**: PostgreSQL via **Supabase** (free tier: 500MB, unlimited API calls)
- **Development**: SQLite (local, zero setup)
- **ORM**: SQLAlchemy (works with both)

### Hosting (100% Free)
| Service | Purpose | Free Tier |
|---------|---------|----------|
| **Render.com** | Backend API + WebSocket server | 750 hrs/month (1 service always on) |
| **Vercel** or **Netlify** | Frontend PWA (static) | Unlimited free |
| **Supabase** | PostgreSQL database | 500MB, no credit card |
| **Cloudinary** | Image/file storage | 10GB free |
| **SendGrid** | Email notifications | Free: 100 emails/day forever |

### Version Control
- GitHub: https://github.com/tabgab/CondoManager.git
- Secrets managed via environment variables (never committed)

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENTS                                   │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌───────────────┐  │
│  │ Web PWA  │  │ Telegram │  │  WhatsApp │  │ Email Client  │  │
│  │(React)   │  │   Bot    │  │  (Meta)   │  │               │  │
│  └────┬─────┘  └────┬─────┘  └─────┬─────┘  └──────┬────────┘  │
└───────┼─────────────┼──────────────┼────────────────┼───────────┘
        │             │              │                │
        ▼             ▼              ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (Render.com)                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐  │
│  │ REST API   │  │ WebSocket  │  │ Bot        │  │ Email    │  │
│  │ /api/v1/   │  │ /ws/       │  │ Handlers   │  │ Handler  │  │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └────┬─────┘  │
│        └───────────────┴───────────────┴───────────────┘        │
│                              │                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   Business Logic Layer                    │   │
│  │  Auth | Users | Reports | Tasks | Notifications | Ledger │   │
│  └──────────────────────────┬───────────────────────────────┘   │
│                              │                                   │
└──────────────────────────────┼──────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌───────────────┐  ┌────────────────────┐  ┌──────────────────┐
│  PostgreSQL   │  │    Cloudinary      │  │  External APIs   │
│  (Supabase)   │  │  (File Storage)    │  │  Telegram/WA     │
└───────────────┘  └────────────────────┘  └──────────────────┘
```

---

## User Roles

| Role | Code | Capabilities |
|------|------|--------------|
| **Super Admin** | `super_admin` | Full system access, manage all managers |
| **Condo Manager** | `manager` | Manage reports, tasks, employees, config |
| **Employee** | `employee` | View/update assigned tasks |
| **Apartment Owner** | `owner` | Submit/view own reports |
| **Tenant** | `tenant` | Same as owner but linked to apartment |

---

## Communication Channels

### Web App (Primary)
- React PWA, works offline for viewing
- Push notifications via browser Web Push API
- Full feature access for all roles

### Telegram Bot
- Owners submit problems via bot (with photo)
- Employees receive task assignments
- Managers get notifications and can approve via inline buttons
- Config: BotFather token stored in settings

### WhatsApp (Meta Cloud API)
- Free business messaging
- Same flows as Telegram (submit, notify, approve)
- Requires Meta Business account + phone number verification

### Email
- **Primary**: SendGrid REST API (free: 100 emails/day)
- **Alternative**: Resend (free: 3,000/month)
- **Fallback**: Gmail App Password with aiosmtplib (requires 2FA on account)
- Confirmation emails, status updates, HTML templates

---

## Security
- All passwords hashed with bcrypt
- JWT tokens (access: 30min, refresh: 7 days)
- Role-based access control (RBAC) on every endpoint
- File uploads: type validation + size limits (10MB)
- Rate limiting on public endpoints
- HTTPS enforced in production
- Secrets: environment variables only, never in git

---

## Deployment Strategy

### GitHub Actions CI/CD
```
Push to main → Run tests → Deploy backend to Render → Deploy frontend to Vercel
```

### Environment Variables (never committed)
- `DATABASE_URL` - Supabase PostgreSQL connection string
- `SECRET_KEY` - JWT signing key
- `TELEGRAM_BOT_TOKEN` - Telegram bot token
- `WHATSAPP_API_TOKEN` - Meta WhatsApp token
- `SENDGRID_API_KEY` - SendGrid API key (recommended alternative)
- `CLOUDINARY_URL` - Cloudinary connection string
- `FRONTEND_URL` - Production frontend URL
