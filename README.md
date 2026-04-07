# CondoManager

![CI](https://github.com/tabgab/CondoManager/workflows/CI/badge.svg)
[![Deploy Status](https://img.shields.io/badge/deploy-ready-success)](https://github.com/tabgab/CondoManager/blob/main/docs/DEPLOYMENT.md)
[![Tech Stack](https://img.shields.io/badge/stack-FastAPI%20%7C%20React%20%7C%20PostgreSQL-blue)](https://github.com/tabgab/CondoManager/blob/main/docs/ARCHITECTURE.md)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot%20Ready-2AABEE?logo=telegram)](https://t.me/your_bot_username)

A multi-role condominium management platform connecting **Apartment Owners/Tenants**, **Employees**, and **Condo Managers**.

## 🚀 Quick Start

### Deploy to Production (Free Tier)

1. **Fork/Clone** this repository
2. **Create Accounts**: [Supabase](https://supabase.com) · [Render](https://render.com) · [Vercel](https://vercel.com)
3. **Deploy** following [docs/PRODUCTION_CHECKLIST.md](docs/PRODUCTION_CHECKLIST.md) (~2 hours)
4. **Total Cost**: $0/month for small buildings

### Run Locally

```bash
# 1. Clone
git clone https://github.com/tabgab/CondoManager.git
cd CondoManager

# 2. Backend
cd backend
cp .env.example .env
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head  # Run migrations
uvicorn app.main:app --reload

# 3. Frontend (new terminal)
cd ../frontend
npm install
npm run dev

# 4. Open http://localhost:5173
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Tech stack, hosting, system diagram, security |
| [docs/DATA_MODEL.md](docs/DATA_MODEL.md) | Database schema, relationships, state machines |
| [docs/API_DESIGN.md](docs/API_DESIGN.md) | REST API endpoints, request/response formats |
| [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) | Phased roadmap, tasks, QA checklists |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Production deployment guide |
| [docs/PRODUCTION_CHECKLIST.md](docs/PRODUCTION_CHECKLIST.md) | Step-by-step deployment checklist |

## 🛠 Technology Stack

| Layer | Technology | Provider | Cost |
|-------|------------|----------|------|
| **Frontend** | React 18 + TypeScript + Tailwind CSS + Vite | Vercel | Free |
| **Backend** | Python FastAPI + SQLAlchemy (async) | Render | Free |
| **Database** | PostgreSQL 15 | Supabase | Free (500MB) |
| **ORM/Migrations** | SQLAlchemy + Alembic | - | - |
| **Auth** | JWT (python-jose) + bcrypt | - | - |
| **Real-time** | WebSocket + Web Push (VAPID) | - | - |
| **Storage** | Cloudinary | Cloudinary | Free (25GB) |
| **Notifications** | Telegram Bot API | Telegram | Free |
| **Email** | SendGrid/Resend/SMTP | SendGrid | Free (100/day) |
| **Testing** | pytest + Vitest + React Testing Library | - | - |

## ✅ Development Status

| Phase | Status | Features |
|-------|--------|----------|
| Phase 0: Foundation | ✅ Complete | GitHub, CI/CD, scaffold |
| Phase 1: Core Backend | ✅ Complete | Auth, RBAC, Buildings, Apartments, Reports |
| Phase 2: Task Management | ✅ Complete | Tasks, Updates, Recurring Tasks |
| Phase 3: Notifications | ✅ Complete | Email, WebSocket, Web Push, Telegram |
| Phase 4: Frontend | ✅ Complete | React app, Dashboards, Forms |
| Phase 5: Telegram Bot | ✅ Complete | /report, /status, Notifications |
| Phase 6: Deployment | ✅ Complete | Supabase, Render, Vercel, Docker |

**Total Tests**: 272 passing ✅  
**Latest Version**: v1.0.0 (deployment ready)

## 🎯 Key Features

- **Multi-Role System**: Manager, Employee, Owner, Tenant, Super Admin
- **Report Management**: Owners submit issues, managers acknowledge/reject, create tasks
- **Task Assignment**: Assign to employees, track progress, handle concerns
- **Real-time Updates**: WebSocket notifications for status changes
- **Telegram Bot**: Submit reports and check status via chat
- **Recurring Tasks**: Weekly cleaning, monthly maintenance schedules
- **Web Push**: Browser notifications for updates
- **Photo Uploads**: Cloudinary integration for report attachments
- **Mobile-First**: PWA with offline support

## 📦 Environment Variables

Copy `.env.production` templates and fill in your values. **Never commit `.env` files to git.**

```bash
# Backend
cp backend/.env.production backend/.env
# Edit with: DATABASE_URL, JWT_SECRET_KEY, TELEGRAM_BOT_TOKEN, etc.

# Frontend  
cp frontend/.env.production frontend/.env
# Edit with: VITE_API_URL, VITE_WS_URL, VITE_TELEGRAM_BOT_USERNAME
```

## 🏗️ Architecture Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Owner     │     │   Manager   │     │  Employee   │
│  (Web/App)  │     │  (Web/App)  │     │  (Web/App)  │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                    │
       └─────────┬─────────┼────────────────────┘
                 │         │
         ┌───────▼─────────▼───────┐
         │   Vercel Frontend       │
         │   (React + PWA)         │
         └───────────┬─────────────┘
                     │
         ┌───────────▼───────────┐
         │   Render Backend      │
         │   (FastAPI + API)     │
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │   Supabase PostgreSQL │
         │   (Data + Auth)       │
         └───────────────────────┘
```

## 🔒 Security

- JWT authentication with refresh tokens
- Role-based access control (RBAC)
- Password hashing with bcrypt
- HTTPS enforced in production
- CORS configured per environment
- Telegram webhook signature verification
- Environment variables for secrets
- Never commit `.env` files

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`npm test -- --run` in frontend, `pytest` in backend)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent async Python framework
- React Query for server state management
- shadcn/ui for beautiful components
- Supabase, Render, Vercel for free hosting tiers

---

**Made with ❤️ for condominium communities worldwide**
