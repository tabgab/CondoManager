# CondoManager - Implementation Plan

## Development Methodology
- **TDD**: All features developed test-first (pytest for backend, Vitest for frontend)
- **Agent Workflow**: PM → Architect → Developer → QA sign-off → Integration
- **Git Branching**: `main` (production), `develop` (integration), `feature/*` branches
- **CI/CD**: GitHub Actions → auto-deploy on merge to `main`

---

## Email Service Selection

| Provider | Free Tier | Best For | Setup |
|----------|-----------|----------|-------|
| **SendGrid** | 100 emails/day forever | SMTP relay via API | Low - just API key |
| **Resend** | 3,000 emails/month forever | Modern API, high deliverability | Low - just API key |
| **Gmail SMTP** | Account limit | Fallback, existing Gmail use | Medium - requires 2FA + App Password |

**Recommendation**: Start with **SendGrid**, migrate to **Resend** if volume grows. Gmail SMTP is fallback only (we have `budakalásztanito38@gmail.com` for testing).

## Phase Overview

| Phase | Name | Description | Est. Effort |
|-------|------|-------------|-------------|
| 0 | **Foundation** | Project setup, CI/CD, DB migrations | Small |
| 1 | **Core Backend** | Auth, Users, Buildings, Reports API | Medium |
| 2 | **Task Management** | Tasks, Recurring, Concerns, Ledger | Medium |
| 3 | **Frontend - Auth & Shell** | PWA setup, login, navigation | Medium |
| 4 | **Frontend - Manager Views** | Dashboard, Reports, Tasks, Users | Large |
| 5 | **Frontend - Employee Views** | Task list, weekly view, updates | Medium |
| 6 | **Frontend - Owner Views** | Submit report, status tracking | Medium |
| 7 | **Notifications** | Email, WebSocket/Web Push | Medium |
| 8 | **Telegram Bot** | Bot integration, all flows | Medium |
| 9 | **WhatsApp** | Meta Cloud API integration | Medium |
| 10 | **Channel Config UI** | Settings page for all channels | Small |
| 11 | **Reports & Analytics** | Reporting, export, dashboards | Medium |
| 12 | **Deployment** | Render + Vercel + Supabase + GitHub CI | Small |
| 13 | **QA & Polish** | Full integration test, bug fixes | Medium |

---

## Phase 0: Foundation

### Goals
- Repository structure initialized
- Local dev environment working
- Database connection established
- CI/CD pipeline skeleton

### Tasks
- [ ] 0.1 Initialize GitHub repo structure
  - `/backend` - FastAPI application
  - `/frontend` - React + Vite PWA
  - `/docs` - Planning documents
  - `docker-compose.yml` - Local dev (Postgres + backend + frontend)
  - `.env.example` - All required env vars documented
  - `.gitignore` - No secrets committed
- [ ] 0.2 Backend scaffold
  - FastAPI app factory pattern
  - SQLAlchemy async engine setup
  - Alembic migration setup
  - Pytest configuration
  - Health check endpoint (`GET /health`)
- [ ] 0.3 Frontend scaffold
  - Vite + React + TypeScript
  - Tailwind CSS configured
  - shadcn/ui initialized
  - Vite PWA plugin configured
  - Vitest configured
  - React Router + basic shell
- [ ] 0.4 Docker Compose for local dev
  - PostgreSQL service
  - Backend service (hot reload)
  - Frontend service (HMR)
- [ ] 0.5 GitHub Actions CI skeleton
  - On push: run backend tests
  - On push: run frontend tests
  - On merge to main: deploy hooks

### QA Checklist (Phase 0)
- [ ] `docker-compose up` starts all services without errors
- [ ] `GET /health` returns `{"status": "ok"}`
- [ ] All Alembic migrations run clean
- [ ] Frontend loads at `http://localhost:5173`
- [ ] CI pipeline runs and passes on GitHub

---

## Phase 1: Core Backend - Auth, Users, Buildings

### Goals
- Full authentication system
- User management CRUD
- Building/Apartment management
- Report submission and management

### Tasks
- [ ] 1.1 User model + Alembic migration
- [ ] 1.2 Auth endpoints
  - `POST /api/v1/auth/register` (invite-only, by manager)
  - `POST /api/v1/auth/login` → JWT access + refresh tokens
  - `POST /api/v1/auth/refresh`
  - `POST /api/v1/auth/logout`
  - `POST /api/v1/auth/forgot-password`
  - `POST /api/v1/auth/reset-password`
- [ ] 1.3 User management endpoints (manager/admin only)
  - `GET /api/v1/users` - list with filters
  - `POST /api/v1/users` - create user
  - `GET /api/v1/users/{id}`
  - `PUT /api/v1/users/{id}`
  - `DELETE /api/v1/users/{id}` (soft delete)
  - `GET /api/v1/users/me` - current user profile
  - `PUT /api/v1/users/me` - update own profile
- [ ] 1.4 Building + Apartment endpoints
  - `GET/POST /api/v1/buildings`
  - `GET/PUT/DELETE /api/v1/buildings/{id}`
  - `GET/POST /api/v1/buildings/{id}/apartments`
  - `GET/PUT/DELETE /api/v1/apartments/{id}`
  - `POST /api/v1/apartments/{id}/assign-user`
- [ ] 1.5 Report endpoints
  - `POST /api/v1/reports` - submit report (owner/tenant)
  - `GET /api/v1/reports` - list (filtered by role)
  - `GET /api/v1/reports/{id}` - detail
  - `PUT /api/v1/reports/{id}/acknowledge` - manager
  - `PUT /api/v1/reports/{id}/reject` - manager (with reason)
  - `DELETE /api/v1/reports/{id}` - owner soft-delete (with reason)
  - `POST /api/v1/reports/{id}/messages` - add thread message
  - `GET /api/v1/reports/{id}/messages`
  - `POST /api/v1/reports/{id}/attachments` - upload file
- [ ] 1.6 RBAC middleware (role-based access decorators)
- [ ] 1.7 Write tests for ALL endpoints (TDD: tests first)

### QA Checklist (Phase 1)
- [ ] All auth flows tested: register, login, refresh, logout, password reset
- [ ] RBAC enforced: owner cannot access manager endpoints
- [ ] File upload: type validation, size limit enforced
- [ ] Report state machine transitions validated
- [ ] All pytest tests pass with >90% coverage

---

## Phase 2: Task Management Backend

### Goals
- Full task lifecycle management
- Recurring task scheduling
- Task concerns system
- Ledger/event log

### Tasks
- [ ] 2.1 Task model + migrations
- [ ] 2.2 Task CRUD endpoints
  - `POST /api/v1/tasks` - create from report or standalone (manager)
  - `GET /api/v1/tasks` - list (filtered by role, status, assignee)
  - `GET /api/v1/tasks/{id}`
  - `PUT /api/v1/tasks/{id}` - update (partial, role-based fields)
  - `PUT /api/v1/tasks/{id}/assign` - assign/reassign employee (manager)
  - `PUT /api/v1/tasks/{id}/start` - employee starts task
  - `PUT /api/v1/tasks/{id}/progress` - update progress % + note
  - `PUT /api/v1/tasks/{id}/complete` - employee marks complete
  - `PUT /api/v1/tasks/{id}/approve` - manager sign-off
  - `PUT /api/v1/tasks/{id}/cancel`
- [ ] 2.3 Task concerns endpoints
  - `POST /api/v1/tasks/{id}/concerns` - employee raises concern
  - `GET /api/v1/tasks/{id}/concerns`
  - `PUT /api/v1/tasks/{id}/concerns/{cid}/resolve` - manager resolves
- [ ] 2.4 Recurring schedules
  - `GET/POST /api/v1/schedules`
  - `GET/PUT/DELETE /api/v1/schedules/{id}`
  - APScheduler job: auto-generate task instances from schedules
- [ ] 2.5 Ledger events
  - Automatic event logging on all state changes
  - `GET /api/v1/ledger` - filterable event log (manager/admin)
- [ ] 2.6 Task update history
  - `GET /api/v1/tasks/{id}/history`
- [ ] 2.7 Write tests for all (TDD)

### QA Checklist (Phase 2)
- [ ] Task state machine transitions enforced server-side
- [ ] Recurring task instances generated correctly by scheduler
- [ ] Ledger events written for every state change
- [ ] Concern flow: raise → manager notified → resolve works
- [ ] Role restrictions verified: employees cannot approve tasks

---

## Phase 3: Frontend Shell & Auth

### Goals
- PWA installable on all platforms
- Login/logout/password reset flows
- Role-aware navigation
- Base layout components

### Tasks
- [ ] 3.1 PWA manifest + service worker
- [ ] 3.2 Auth pages: Login, Forgot Password, Reset Password
- [ ] 3.3 JWT management: auto-refresh, secure storage
- [ ] 3.4 Role-based route guards
- [ ] 3.5 Base layout: sidebar navigation (role-specific menus)
- [ ] 3.6 User profile page
- [ ] 3.7 Toast notifications component
- [ ] 3.8 Write Vitest component tests

---

## Phase 4: Frontend - Manager Dashboard

### Goals
- Full manager workflow in the web app

### Tasks
- [ ] 4.1 Dashboard: open reports, pending tasks, quick stats
- [ ] 4.2 Reports list: filter by status, search, sort
- [ ] 4.3 Report detail: view, message thread, attachments, action buttons
- [ ] 4.4 Create task from report (dialog/modal)
- [ ] 4.5 Task list: filter, sort, assign, bulk actions
- [ ] 4.6 Task detail: history timeline, concerns, approve button
- [ ] 4.7 Recurring schedules: create, edit, enable/disable
- [ ] 4.8 User management: list, create, edit, deactivate
- [ ] 4.9 Building/apartment management
- [ ] 4.10 Ledger/event log viewer with filters

---

## Phase 5: Frontend - Employee Views

### Tasks
- [ ] 5.1 My tasks list: filtered to assigned tasks
- [ ] 5.2 Weekly task calendar view
- [ ] 5.3 Task detail: update progress, mark complete, raise concern
- [ ] 5.4 Concern submission form
- [ ] 5.5 Notification panel

---

## Phase 6: Frontend - Owner/Tenant Views

### Tasks
- [ ] 6.1 Submit report form: title, description, photo upload, apartment selector
- [ ] 6.2 My reports list with status indicators
- [ ] 6.3 Report detail: status timeline, message thread, delete with reason
- [ ] 6.4 Status display: accepted, assigned (to whom), progress %, days since accepted
- [ ] 6.5 Status history log for each report

---

## Phase 7: Notifications

### Tasks
- [ ] 7.1 WebSocket connection: real-time in-app notifications
- [ ] 7.2 Notification bell + dropdown in navbar
- [ ] 7.3 Browser Web Push API (PWA push notifications)
- [ ] 7.4 Email notification service (aiosmtplib + Gmail)
  - HTML email templates for each notification type
  - Async email queue
- [ ] 7.5 Notification preferences page (user can toggle channels)
- [ ] 7.6 Test all notification flows end-to-end

---

## Phase 8: Telegram Bot

### Tasks
- [ ] 8.1 Bot setup: python-telegram-bot v20 async
- [ ] 8.2 /start command: link Telegram account to system user
- [ ] 8.3 Owner flow: submit problem via bot with photo
- [ ] 8.4 Manager notifications: new report alert with inline approve/reject buttons
- [ ] 8.5 Employee notifications: task assigned with inline start/update buttons
- [ ] 8.6 Status update commands
- [ ] 8.7 Webhook setup for production (vs polling for dev)
- [ ] 8.8 Bot configuration page in settings (paste bot token, copy webhook URL)

---

## Phase 9: WhatsApp Integration

### Tasks
- [ ] 9.1 Meta Cloud API setup and webhook handler
- [ ] 9.2 Account linking: phone number verification
- [ ] 9.3 Replicate Telegram flows for WhatsApp
- [ ] 9.4 WhatsApp configuration page (guided setup wizard)

---

## Phase 10: Channel Configuration UI

### Tasks
- [ ] 10.1 Settings page: channel list with enable/disable toggles
- [ ] 10.2 Telegram config: token field, webhook URL to copy, test button
- [ ] 10.3 WhatsApp config: wizard-style guided setup
- [ ] 10.4 Email config: SMTP settings, test email button
- [ ] 10.5 Web Push: auto-configured, show subscription status
- [ ] 10.6 Each channel shows connection status (connected/error/not configured)

---

## Phase 11: Reports & Analytics

### Tasks
- [ ] 11.1 Manager: open/closed task summary dashboard
- [ ] 11.2 Manager: report-to-task conversion rate
- [ ] 11.3 Manager: employee workload view
- [ ] 11.4 Employee: personal completed task history
- [ ] 11.5 Owner: full history of their submitted reports
- [ ] 11.6 Export to CSV/PDF (manager only)
- [ ] 11.7 Date range filters on all reports

---

## Phase 12: Production Deployment

### Tasks
- [ ] 12.1 Supabase project setup + schema migration
- [ ] 12.2 Cloudinary account + config
- [ ] 12.3 Render.com backend deployment + env vars
- [ ] 12.4 Vercel frontend deployment
- [ ] 12.5 GitHub Actions full CI/CD pipeline
- [ ] 12.6 Domain/HTTPS verification
- [ ] 12.7 Seed initial super_admin account
- [ ] 12.8 Smoke test all production endpoints

---

## Phase 13: QA & Polish

### Tasks
- [ ] 13.1 Full end-to-end test run (all user roles, all flows)
- [ ] 13.2 Mobile UX review (iPhone + Android)
- [ ] 13.3 Accessibility audit
- [ ] 13.4 Performance: API response times, frontend bundle size
- [ ] 13.5 Security: auth bypass attempts, file upload exploits
- [ ] 13.6 Error handling: all edge cases covered
- [ ] 13.7 Documentation: README, API docs, user guide

---

## Agent Assignment Matrix

| Phase | Lead Agent | Support |
|-------|-----------|--------|
| 0 | Developer | Architect review |
| 1-2 | Developer (backend) | QA sign-off |
| 3-6 | Developer (frontend) | UI Design, QA sign-off |
| 7-9 | Developer (integrations) | QA sign-off |
| 10-11 | Developer | UI Design, QA sign-off |
| 12 | Developer | Architect review |
| 13 | QA | All agents |

---

## Definition of Done (per feature)
1. Unit tests written and passing
2. Integration test written and passing
3. Code reviewed against DATA_MODEL.md and API_DESIGN.md
4. QA agent has signed off
5. No console errors or warnings
6. Merged to `develop` branch
