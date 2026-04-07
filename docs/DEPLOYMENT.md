# CondoManager Deployment Guide

This guide will walk you through deploying CondoManager to production using free-tier services.

## Overview

We use the following services (all free tier):
- **Supabase**: PostgreSQL database
- **Render**: Backend web service
- **Vercel**: Frontend hosting
- **Cloudinary**: Image storage
- **Telegram Bot**: Notifications
- **SendGrid**: Email (optional)

## Step 1: Create Supabase Project

1. Go to https://supabase.com
2. Click "New Project"
3. Create an organization if you don't have one
4. Fill in project details:
   - **Name**: condomanager
   - **Database Password**: Generate a strong password
   - **Region**: Choose one close to your users
   - **Pricing Plan**: Free
5. Wait for project creation (1-2 minutes)

### Get Connection String

1. In your Supabase dashboard, go to **Settings → Database**
2. Scroll to **Connection string**
3. Copy the **URI** format string:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@[HOST].supabase.co:5432/postgres
   ```
4. Save this for later (it's your `DATABASE_URL`)

### Important: Enable Extensions

1. In Supabase SQL Editor, run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
   ```

## Step 2: Set Up Environment Variables

### Backend Configuration

Create `backend/.env.production`:

```bash
# Database (from Supabase)
DATABASE_URL=postgresql://postgres:[password]@[host].supabase.co:5432/postgres

# JWT (generate with: openssl rand -hex 32)
JWT_SECRET_KEY=your_generated_secret_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Web Push VAPID Keys (generate with scripts/generate_vapid_keys.py)
VAPID_PUBLIC_KEY=your_public_key_here
VAPID_PRIVATE_KEY=your_private_key_here

# Telegram Bot Token (already configured)
TELEGRAM_BOT_TOKEN=8704250728:AAENUk2pNbxnNzl3NEkBW1v2ysdA7Ly2zuU

# Email (optional - from SendGrid)
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=your_sendgrid_api_key_here
DEFAULT_FROM_EMAIL=noreply@condomanager.app

# Frontend URL (update after Vercel deployment)
FRONTEND_URL=https://condomanager.vercel.app

# Production settings
ENVIRONMENT=production
LOG_LEVEL=info
```

### Generate Required Keys

#### 1. JWT Secret
```bash
openssl rand -hex 32
```

#### 2. VAPID Keys
```bash
cd backend
python scripts/generate_vapid_keys.py
```

This outputs:
```
VAPID_PUBLIC_KEY=BJLkJ3r...
VAPID_PRIVATE_KEY=MIGHAgEAMBM...
```

Copy these to your `.env.production`

## Step 3: Deploy Backend to Render

### Setup Render Account

1. Go to https://render.com
2. Sign up (can use GitHub login)
3. Click "New +" → **Blueprint**
4. Connect your GitHub repository
5. Render will detect `render.yaml` and suggest services

### Manual Service Creation (Alternative)

If Blueprint doesn't work:

1. Click "New +" → **Web Service**
2. Connect your GitHub repo
3. Configure:
   - **Name**: condomanager-backend
   - **Environment**: Python
   - **Plan**: Free
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. Add Environment Variables:
   - Add all variables from `.env.production`

5. Deploy Web Service

### Create PostgreSQL Database on Render (Alternative to Supabase)

If you prefer Render's PostgreSQL:

1. Click "New +" → **PostgreSQL**
2. Name: `condomanager-db`
3. Plan: Free
4. Copy the "Internal Connection String"
5. Use this as your `DATABASE_URL`

## Step 4: Run Database Migrations

### After First Deploy

Once your backend is deployed, run migrations:

```bash
# Option 1: Render Shell
1. Go to your service dashboard
2. Click "Shell" tab
3. Run: alembic upgrade head

# Option 2: Local with remote DB
export DATABASE_URL=your_supabase_database_url
cd backend
alembic upgrade head
```

### Initial Admin User

After migrations, create an admin user:

```bash
# In Render shell or locally
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
        print(f'Created admin user: {user.email}')

asyncio.run(create_admin())
"
```

## Step 5: Deploy Frontend to Vercel

1. Go to https://vercel.com
2. Sign up with GitHub
3. Click "Add New Project"
4. Import your CondoManager repository
5. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
6. Add Environment Variables:
   - `VITE_API_URL`: Your Render backend URL (e.g., `https://condomanager-backend.onrender.com/api/v1`)
7. Click Deploy

### Frontend Environment Variables

Create `frontend/.env.production`:

```bash
VITE_API_URL=https://condomanager-backend.onrender.com/api/v1
VITE_APP_NAME=CondoManager
VITE_TELEGRAM_BOT_USERNAME=your_bot_username
```

## Step 6: Configure Telegram Webhook

After backend deployment:

```bash
curl -X POST "https://api.telegram.org/bot8704250728:AAENUk2pNbxnNzl3NEkBW1v2ysdA7Ly2zuU/setWebhook" \
  -d "url=https://your-backend.onrender.com/telegram/webhook"
```

Verify webhook:
```bash
curl "https://api.telegram.org/bot8704250728:AAENUk2pNbxnNzl3NEkBW1v2ysdA7Ly2zuU/getWebhookInfo"
```

## Step 7: Cloudinary Setup (Optional)

For image uploads:

1. Go to https://cloudinary.com
2. Sign up for free account
3. Get your Cloud Name, API Key, API Secret
4. Add to backend `.env.production`:
   ```
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret
   ```

## Step 8: Email Setup (Optional)

### SendGrid Option

1. Go to https://sendgrid.com
2. Create free account (100 emails/day)
3. Create API Key
4. Verify sender email
5. Add to environment:
   ```
   EMAIL_PROVIDER=sendgrid
   SENDGRID_API_KEY=your_api_key
   DEFAULT_FROM_EMAIL=noreply@condomanager.app
   ```

### Using Existing Gmail (for testing)

For the test email (budakalásztanito38@gmail.com):

1. Enable 2FA on Gmail
2. Generate App Password
3. Add to environment:
   ```
   EMAIL_PROVIDER=smtp
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=budakalásztanito38@gmail.com
   SMTP_PASSWORD=your_app_password
   ```

## Step 9: Web Push Setup

Already enabled with VAPID keys generated in Step 2.

To subscribe users:
1. Frontend automatically requests push notification permission
2. VAPID keys authenticate the server

## Verification Checklist

After deployment, verify:

- [ ] Backend health endpoint responds: `GET https://your-backend.onrender.com/health`
- [ ] Database migrations ran successfully
- [ ] Admin user can log in
- [ ] Frontend loads at Vercel URL
- [ ] Login works from frontend
- [ ] Telegram bot responds to /start
- [ ] Can submit report via Telegram
- [ ] Can link Telegram account (via web app)

## Troubleshooting

### Database Connection Issues

**Problem**: Can't connect to Supabase
```
asyncpg.exceptions.InvalidAuthorizationSpecificationError: connection failed
```

**Solution**:
1. Verify password in DATABASE_URL
2. Check if IP is allowed (Supabase → Settings → Database → Network Restrictions)
3. Use IPv4 connection string if IPv6 is blocked

### Telegram Webhook Not Working

**Problem**: Bot not receiving messages

**Solution**:
1. Check webhook is set: `getWebhookInfo`
2. Verify SSL certificate is valid (Telegram requires HTTPS)
3. Check backend logs for webhook errors

### Alembic Migration Failures

**Problem**: Migration fails on Supabase

**Solution**:
1. Ensure `uuid-ossp` extension is enabled
2. Check migration files for unsupported SQL
3. Run migrations manually: `alembic upgrade +1` step by step

## Production Security Checklist

- [ ] Change default admin password immediately
- [ ] Enable Supabase Row Level Security (RLS)
- [ ] Set strong JWT secret (min 32 chars)
- [ ] Enable logging and monitoring
- [ ] Set up database backups
- [ ] Configure CORS properly (frontend-only origin)
- [ ] Don't commit `.env.production` to git
- [ ] Enable HTTPS redirect (Render does this automatically)

## Cost Estimates (Free Tier)

| Service | Free Tier Limits |
|---------|-----------------|
| Supabase | 500MB DB, 2GB bandwidth |
| Render | 750 hours/month, sleeps after 15 min inactivity |
| Vercel | Unlimited deployments, 100GB bandwidth |
| Cloudinary | 25GB storage, 25 credits |
| SendGrid | 100 emails/day |
| Telegram | Unlimited messages |

**Total Cost**: $0/month for small condo buildings

## Next Steps

1. Invite building managers to create accounts
2. Add buildings and apartments via admin panel
3. Configure recurring tasks (cleaning, maintenance)
4. Train employees on Telegram task notifications
5. Set up owner accounts and link their Telegram

## Support

If you encounter issues:
1. Check logs in Render dashboard
2. Review Supabase database logs
3. Test API endpoints with curl/Postman
4. Verify all environment variables are set

---

**Note**: This is a living document. Update it as your deployment evolves!
