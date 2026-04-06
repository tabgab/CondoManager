# CondoManager

![CI](https://github.com/tabgab/CondoManager/workflows/CI/badge.svg)

A multi-role condominium management platform connecting **Apartment Owners/Tenants**, **Employees**, and **Condo Managers**.

## Documentation

| Document | Description |
|----------|-------------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Tech stack, hosting, system diagram, security |
| [docs/DATA_MODEL.md](docs/DATA_MODEL.md) | Database schema, relationships, state machines |
| [docs/API_DESIGN.md](docs/API_DESIGN.md) | REST API endpoints, request/response formats |
| [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) | Phased roadmap, tasks, QA checklists |

## Quick Stack Summary

- **Frontend**: React 18 + TypeScript + Tailwind CSS PWA (Vercel)
- **Backend**: Python FastAPI + SQLAlchemy (Render.com)
- **Database**: PostgreSQL (Supabase free tier)
- **Storage**: Cloudinary (free tier)
- **Channels**: Web PWA, Telegram Bot, WhatsApp (Meta), Email (Gmail)
- **Hosting**: 100% free tier services

## Development Status

Currently in planning phase. See [IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) for full roadmap.

## Setup

> Instructions will be added as phases complete.

## Environment Variables

Copy `.env.example` to `.env` and fill in values. **Never commit `.env` to git.**
