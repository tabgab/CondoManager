# CondoManager Production Deployment Checklist

This checklist ensures a complete, verified production deployment of CondoManager.

**Last Updated**: 2026-04-07  
**Estimated Time**: 2-3 hours (first deployment)  
**Complexity**: Medium (multiple services)

---

## Pre-Deployment ✅

### 1. Repository Preparation
- [ ] All code committed to `main` branch
- [ ] `.env.production` files created (not committed)
- [ ] All tests passing locally
- [ ] CI/CD pipeline green (GitHub Actions)
- [ ] No sensitive data in repository

### 2. Account Setup

#### GitHub
- [ ] Repository at https://github.com/tabgab/CondoManager.git accessible
- [ ] GitHub Actions enabled

#### Supabase
- [ ] Account created at https://supabase.com
- [ ] New project created (condomanager)
- [ ] Database password secured (password manager)
- [ ] Connection string copied

#### Render
- [ ] Account created at https://render.com
- [ ] GitHub connected to Render

#### Vercel
- [ ] Account created at https://vercel.com
- [ ] GitHub connected to Vercel

#### Telegram Bot
- [ ] Bot created with @BotFather
- [ ] Bot token secured: `8704250728:AAENUk2pNbxnNzl3NEkBW1v2ysdA7Ly2zuU`
- [ ] Bot username noted (e.g., @condomanagertest_bot)

#### SendGrid (Optional)
- [ ] Account created at https://sendgrid.com
- [ ] API key generated
- [ ] Sender email verified

---

## Deployment Steps 🚀

### Step 1: Database Setup (Supabase)

1. [ ] Create Supabase project
2. [ ] Run in SQL Editor:
   ```sql
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
   ```
3. [ ] Copy connection string:
   ```
   postgresql://postgres:[PASSWORD]@[PROJECT-REF].supabase.co:5432/postgres
   ```
4. [ ] Add to `backend/.env.production`:
   ```
   DATABASE_URL=postgresql://postgres:xxx@xxx.supabase.co:5432/postgres
   ```

**Time**: 15 minutes

### Step 2: Backend Deployment (Render)

1. [ ] Go to Render Dashboard → New + → Blueprint
2. [ ] Select GitHub repository
3. [ ] Render detects `render.yaml`
4. [ ] Configure environment variables:
   - `DATABASE_URL` (from Supabase)
   - `JWT_SECRET_KEY` (generate: `openssl rand -hex 32`)
   - `VAPID_PUBLIC_KEY` (run `python scripts/generate_vapid_keys.py`)
   - `VAPID_PRIVATE_KEY` (from same script)
   - `TELEGRAM_BOT_TOKEN` (already have)
   - `FRONTEND_URL` (placeholder, update after Vercel)
   - `CORS_ORIGINS` (placeholder, update after Vercel)
5. [ ] Deploy
6. [ ] Wait for build (3-5 minutes)
7. [ ] Get backend URL: `https://condomanager-backend.onrender.com`

**Time**: 20 minutes

### Step 3: Database Migrations

**Option A: Render Shell**
1. [ ] Go to Render service → Shell tab
2. [ ] Run:
   ```bash
   cd /app
   alembic upgrade head
   ```

**Option B: Local with Remote DB**
1. [ ] Set `DATABASE_URL` locally
2. [ ] Run:
   ```bash
   cd backend
   ./scripts/run_migrations.sh
   ```

**Verify**:
- [ ] `alembic current` shows latest revision
- [ ] No errors in output

**Time**: 10 minutes

### Step 4: Frontend Deployment (Vercel)

1. [ ] Go to Vercel Dashboard → Add New Project
2. [ ] Import GitHub repository
3. [ ] Configure:
   - Framework: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. [ ] Add environment variable:
   ```
   VITE_API_URL=https://condomanager-backend.onrender.com/api/v1
   ```
5. [ ] Deploy
6. [ ] Get frontend URL: `https://condomanager.vercel.app`

**Time**: 15 minutes

### Step 5: Environment Variable Sync

**Update Render Backend**:
1. [ ] Go to Render service → Environment
2. [ ] Add/Update:
   ```
   FRONTEND_URL=https://condomanager.vercel.app
   CORS_ORIGINS=https://condomanager.vercel.app
   ```
3. [ ] Redeploy (Render auto-redeploys on env change)

**Time**: 5 minutes

### Step 6: Telegram Webhook Setup

1. [ ] Set webhook:
   ```bash
   curl -X POST "https://api.telegram.org/bot8704250728:AAENUk2pNbxnNzl3NEkBW1v2ysdA7Ly2zuU/setWebhook" \
     -d "url=https://condomanager-backend.onrender.com/telegram/webhook"
   ```

2. [ ] Verify:
   ```bash
   curl "https://api.telegram.org/bot8704250728:AAENUk2pNbxnNzl3NEkBW1v2ysdA7Ly2zuU/getWebhookInfo"
   ```

**Expected Response**:
```json
{
  "ok": true,
  "result": {
    "url": "https://...",
    "has_custom_certificate": false,
    "pending_update_count": 0
  }
}
```

**Time**: 5 minutes

### Step 7: Initial Admin User

**Option A: Render Shell**
1. [ ] Go to Render service → Shell
2. [ ] Run interactive script:
   ```bash
   cd /app
   python scripts/create_admin.py
   ```

**Option B: Manual**
```bash
# In Render Shell or local
python -c "
import asyncio
from app.db.session import get_db_session
from app.crud.user import create_user
from app.schemas.user import UserCreate

async def create_admin():
    async with get_db_session() as db:
        user = await create_user(
            db,
            UserCreate(
                email='admin@condomanager.app',
                password='YourStrongPassword123!',
                first_name='Admin',
                last_name='User',
                role='super_admin',
                phone='+1234567890'
            )
        )
        print(f'Created: {user.email}')

asyncio.run(create_admin())
"
```

**Time**: 5 minutes

---

## Post-Deployment Verification ✅

### API Health Check
- [ ] `GET https://backend.onrender.com/health` returns 200
- [ ] Response includes:
  ```json
  {
    "status": "healthy",
    "database": "connected"
  }
  ```

### Frontend Loading
- [ ] `https://condomanager.vercel.app` loads without errors
- [ ] Login page displays correctly
- [ ] No console errors (F12 → Console)

### Login Flow
- [ ] Login with admin credentials works
- [ ] JWT token stored in localStorage
- [ ] Redirect to ManagerDashboard

### Telegram Bot
- [ ] Send `/start` to bot
- [ ] Receive welcome message
- [ ] Send `/help` - receive command list
- [ ] Send `/report` - start report flow

### Database Connectivity
- [ ] Can create buildings via API
- [ ] Data persists in Supabase

---

## Feature Testing Matrix

| Feature | Manager | Employee | Owner | Telegram |
|---------|---------|----------|-------|----------|
| Login | ⬜ | ⬜ | ⬜ | N/A |
| Create Building | ⬜ | N/A | N/A | N/A |
| Create Apartment | ⬜ | N/A | N/A | N/A |
| Submit Report | N/A | N/A | ⬜ | ⬜ |
| View Reports | ⬜ | ⬜ | ⬜ | ⬜ |
| Acknowledge Report | ⬜ | N/A | N/A | N/A |
| Create Task | ⬜ | N/A | N/A | N/A |
| View Tasks | ⬜ | ⬜ | N/A | N/A |
| Complete Task | ⬜ | ⬜ | N/A | N/A |
| Real-time Updates | ⬜ | ⬜ | ⬜ | ⬜ |

---

## Security Checklist 🔒

- [ ] Admin password changed from default
- [ ] JWT_SECRET_KEY is 32+ random characters
- [ ] VAPID keys generated (not default)
- [ ] Telegram bot token not exposed in logs
- [ ] Database password in password manager
- [ ] `.env.production` files not in git
- [ ] CORS origins restricted to production domain
- [ ] HTTPS enforced (Render/Vercel auto-SSL)
- [ ] Security headers configured (X-Frame-Options, etc.)

---

## Monitoring Setup 📊

### Render Dashboard
- [ ] Enable log streaming
- [ ] Set up alert on high error rates
- [ ] Monitor CPU/memory usage

### Supabase Dashboard
- [ ] Check connection pool health
- [ ] Monitor database size (500MB limit on free tier)

### Uptime Monitoring (Optional)
- [ ] Add to UptimeRobot or Pingdom
- [ ] Monitor: `https://backend.onrender.com/health`

---

## Rollback Plan 🔄

### If Deployment Fails

**Database Issues**:
```bash
# Rollback migration
alembic downgrade -1

# Or reset (CAREFUL - loses data)
dropdb condomanager && createdb condomanager
alembic upgrade head
```

**Backend Issues**:
- Go to Render → Manual Deploy → Previous Commit
- Or set `DEBUG=true` temporarily

**Frontend Issues**:
- Vercel → Deployments → Previous version → Promote

**Full Rollback**:
1. Backup database (if any data)
2. Delete Render service
3. Delete Vercel project
4. Start fresh with checklist

---

## Troubleshooting Quick Reference

### "Cannot connect to database"
- Check `DATABASE_URL` in Render env vars
- Verify Supabase network restrictions
- Test: `psql $DATABASE_URL -c "SELECT 1"`

### "CORS error"
- Verify `CORS_ORIGINS` includes frontend URL
- Check for `https://` vs `http://`
- Redeploy backend after CORS change

### "Telegram bot not responding"
- Check webhook: `getWebhookInfo`
- Verify bot token correct
- Check Render logs for webhook errors

### "Frontend blank / build error"
- Check `VITE_API_URL` in Vercel env
- Verify backend is running
- Check browser console for errors

### "Migration failed"
- Check migration syntax (PostgreSQL vs SQLite differences)
- Ensure `uuid-ossp` extension enabled
- Run: `alembic history` to see migration order

---

## Post-Launch Tasks 🎯

### Week 1
- [ ] Monitor error rates daily
- [ ] Verify all automated tests still pass
- [ ] Create first real building + apartment
- [ ] Test with real users (employees, owners)

### Week 2-4
- [ ] Set up recurring tasks (weekly cleaning, etc.)
- [ ] Train building managers on system
- [ ] Collect user feedback
- [ ] Fix any critical bugs

### Month 2+
- [ ] Review free tier limits
- [ ] Consider paid tier if growing
- [ ] Add more buildings/apartments
- [ ] Expand to additional features

---

## Emergency Contacts 📞

| Service | Support URL | Status Page |
|---------|-------------|-------------|
| Render | https://render.com/docs | https://status.render.com |
| Vercel | https://vercel.com/support | https://www.vercel-status.com |
| Supabase | https://supabase.com/support | https://status.supabase.com |
| Telegram | @BotFather | N/A |
| SendGrid | https://support.sendgrid.com | https://status.sendgrid.com |

---

**Remember**: This is a living document. Update it as you learn from your deployment!

**Next**: See `DEPLOYMENT.md` for detailed configuration instructions.
