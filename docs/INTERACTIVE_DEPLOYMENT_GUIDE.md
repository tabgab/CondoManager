# Interactive Deployment Guide

Step-by-step walkthrough to deploy CondoManager using your new accounts.

---

## Pre-Deployment Checklist

Before starting, ensure you have:
- [ ] Supabase account created (https://supabase.com)
- [ ] Render.com account created (https://render.com)  
- [ ] Vercel account created (https://vercel.com)
- [ ] Telegram bot token (already have: `8704250728:AAENUk2pNbxnNzl3NEkBW1v2ysdA7Ly2zuU`)

Estimated time: **2-3 hours** for first deployment

---

## STEP 1: Supabase PostgreSQL Database (15 minutes)

### 1.1 Create Project
1. Go to https://app.supabase.com
2. Click **"New Project"**
3. Fill in:
   - **Organization**: Create new or select existing
   - **Project Name**: `condomanager` (or `condomanager-prod`)
   - **Database Password**: Click **"Generate a password"** - **COPY THIS PASSWORD NOW!**
   - **Region**: Select closest to your users (e.g., `us-east-1` for US, `eu-west-1` for Europe)
   - **Pricing Plan**: **Free Tier**
4. Click **"Create new project"**
5. Wait 1-2 minutes for database to provision

### 1.2 Get Connection String (CRITICAL)
1. In your project dashboard, click **"Settings"** (left sidebar, gear icon)
2. Click **"Database"** in the submenu
3. Scroll down to **"Connection string"** section
4. Select **"URI"** tab
5. **Copy the connection string** - it looks like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxxxxxxxxxx.supabase.co:5432/postgres
   ```
6. **Paste this in a secure note** - you'll need it 3 times

### 1.3 Enable Required Extension
1. In your project dashboard, click **"SQL Editor"** (left sidebar)
2. Click **"New query"**
3. Paste this SQL:
   ```sql
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
   ```
4. Click **"Run"** (or Ctrl+Enter)
5. Should see: "Success. No rows returned"

### 1.4 Test Connection (Optional but recommended)
```bash
# Install psql if needed
# Test connection:
psql "postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxxxxxxxxxx.supabase.co:5432/postgres" -c "SELECT 1;"
# Should return: ?column?  1
```

---

## STEP 2: Prepare Backend Environment Variables

Before deploying to Render, we need these values ready:

### Required Variables

| Variable | Value | Source |
|----------|-------|--------|
| `DATABASE_URL` | `postgresql://...` | From Step 1.2 |
| `JWT_SECRET_KEY` | Generate new | Run: `openssl rand -hex 32` |
| `TELEGRAM_BOT_TOKEN` | `8704250728:AAENUk2pNbxnNzl3NEkBW1v2ysdA7Ly2zuU` | Already have |
| `VAPID_PRIVATE_KEY` | Generate new | Run `python scripts/generate_vapid_keys.py` |
| `VAPID_PUBLIC_KEY` | Generated with above | Same script |

### Generate Keys Now

Open terminal in project root:

```bash
# 1. Generate JWT Secret
echo "JWT_SECRET_KEY:"
openssl rand -hex 32

# 2. Generate VAPID Keys
cd backend
python scripts/generate_vapid_keys.py
# Copy both PRIVATE and PUBLIC keys
```

Save all these values - you'll paste them into Render in Step 3.

---

## STEP 3: Deploy Backend to Render.com (20 minutes)

### 3.1 Create Web Service
1. Go to https://dashboard.render.com
2. Click **"New +"** (top right)
3. Select **"Web Service"**
4. Connect your GitHub:
   - Click **"Connect GitHub"** if not already connected
   - Authorize Render to access repositories
   - Select repository: `tabgab/CondoManager`
5. Configure service:
   - **Name**: `condomanager-backend` (or `condomanager-api`)
   - **Region**: Same region as your Supabase (e.g., Ohio for us-east-1)
   - **Runtime**: **Python**
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1`
6. Click **"Create Web Service"**

### 3.2 Add Environment Variables (CRITICAL STEP)

After creation, you'll be on the service dashboard. Click **"Environment"** tab:

Add these variables one by one:

**Required:**
```
DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST].supabase.co:5432/postgres
JWT_SECRET_KEY=[32-char-hex-from-step-2]
TELEGRAM_BOT_TOKEN=8704250728:AAENUk2pNbxnNzl3NEkBW1v2ysdA7Ly2zuU
VAPID_PRIVATE_KEY=[private-key-from-step-2]
VAPID_PUBLIC_KEY=[public-key-from-step-2]
```

**Optional but recommended:**
```
FRONTEND_URL=https://condomanager.vercel.app  # Will update after Vercel deploy
CORS_ORIGINS=https://condomanager.vercel.app,https://condomanager-git-*.vercel.app
ENVIRONMENT=production
LOG_LEVEL=INFO
```

**For Email (optional - skip for now):**
```
# If you have SendGrid:
# SENDGRID_API_KEY=SG.xxx
# EMAIL_FROM=noreply@condomanager.app
```

Click **"Save Changes"** after adding all.

### 3.3 Wait for First Deploy
- Render will automatically deploy after saving env vars
- Watch the **"Deploys"** section
- Wait for **"Live"** status (green checkmark)
- Copy the **URL** (e.g., `https://condomanager-backend.onrender.com`)
- **Save this URL** - needed for frontend and Telegram webhook

### 3.4 Test Backend is Live
```bash
# Replace with your actual Render URL:
curl https://YOUR-BACKEND.onrender.com/health
# Expected: {"status":"ok","service":"condomanager-backend"}
```

---

## STEP 4: Run Database Migrations (10 minutes)

### Option A: Via Render Shell (Recommended)
1. In Render dashboard, click your service
2. Click **"Shell"** tab (left sidebar)
3. This opens a terminal in your running container
4. Run migrations:
   ```bash
   cd /opt/render/project/src/backend
   alembic upgrade head
   ```
5. Should see: `Running upgrade 001 -> 002 -> 003...` then `OK`

### Option B: Local with Remote Database
```bash
cd /a0/usr/projects/condomanager/backend
export DATABASE_URL="postgresql://postgres:[PASSWORD]@[HOST].supabase.co:5432/postgres"
alembic upgrade head
```

### Verify Migration Success
In Supabase dashboard:
1. Go to **"Table Editor"** (left sidebar)
2. You should see tables: `users`, `buildings`, `apartments`, `reports`, `tasks`, etc.

---

## STEP 5: Deploy Frontend to Vercel (15 minutes)

### 5.1 Import Project
1. Go to https://vercel.com/dashboard
2. Click **"Add New..."** → **"Project"**
3. Import Git Repository:
   - Find `tabgab/CondoManager`
   - Click **"Import"**
4. Configure project:
   - **Project Name**: `condomanager` (this becomes part of URL)
   - **Framework Preset**: **Vite**
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (should auto-detect)
   - **Output Directory**: `dist` (should auto-detect)
5. Click **"Deploy"**

### 5.2 Add Environment Variables
While deploying (or after in project settings):
1. Go to **"Settings"** → **"Environment Variables"**
2. Add:
   ```
   VITE_API_URL=https://YOUR-BACKEND.onrender.com/api/v1
   VITE_WS_URL=wss://YOUR-BACKEND.onrender.com/ws
   VITE_TELEGRAM_BOT_USERNAME=condomanagertest_bot
   ```
   Replace `YOUR-BACKEND` with your actual Render URL from Step 3.3.

3. Click **"Save"**
4. Vercel will redeploy automatically with new env vars

### 5.3 Wait for Deploy
- Watch the deployment logs
- Should complete in 1-2 minutes
- Copy the **Domain** (e.g., `condomanager.vercel.app`)
- **Save this URL**

### 5.4 Test Frontend
1. Open `https://condomanager.vercel.app` in browser
2. Should see login page
3. Check browser console for errors

---

## STEP 6: Update Backend CORS (5 minutes)

Now that frontend is deployed, backend needs to know about it:

### 6.1 Update Render Environment
1. Go back to Render dashboard
2. Click your backend service
3. Click **"Environment"** tab
4. Update these variables:
   ```
   FRONTEND_URL=https://condomanager.vercel.app
   CORS_ORIGINS=https://condomanager.vercel.app,https://condomanager-git-*.vercel.app
   ```
5. Click **"Save Changes"**
6. This triggers a redeploy (30-60 seconds)

### 6.2 Test CORS
```bash
curl -H "Origin: https://condomanager.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     https://YOUR-BACKEND.onrender.com/auth/login -v
# Should see: Access-Control-Allow-Origin: https://condomanager.vercel.app
```

---

## STEP 7: Set Telegram Webhook (5 minutes)

### 7.1 Set Webhook URL
Replace `YOUR-BACKEND` with your Render URL:

```bash
curl -X POST "https://api.telegram.org/bot8704250728:AAENUk2pNbxnNzl3NEkBW1v2ysdA7Ly2zuU/setWebhook" \
  -d "url=https://YOUR-BACKEND.onrender.com/telegram/webhook"

# Expected response:
# {"ok":true,"result":true,"description":"Webhook was set"}
```

### 7.2 Verify Webhook
```bash
curl "https://api.telegram.org/bot8704250728:AAENUk2pNbxnNzl3NEkBW1v2ysdA7Ly2zuU/getWebhookInfo"

# Should show:
# {"ok":true,"result":{"url":"https://YOUR-BACKEND.onrender.com/telegram/webhook","has_custom_certificate":false...}}
```

### 7.3 Test Bot
1. Open Telegram
2. Search for `@condomanagertest_bot`
3. Click **"Start"** or send `/start`
4. Should receive welcome message
5. Try `/report` - should start report submission flow

---

## STEP 8: Create First Admin User (5 minutes)

### Via Render Shell
1. In Render dashboard, click **"Shell"** tab
2. Run:
   ```bash
   cd /opt/render/project/src/backend
   python scripts/create_admin.py --quick
   ```
   Or interactive mode:
   ```bash
   python scripts/create_admin.py
   ```
3. Enter when prompted:
   - Email: `admin@condomanager.app` (or your email)
   - Password: Strong password (8+ chars, uppercase, lowercase, number, special)
   - First Name: `Admin`
   - Last Name: `User`
4. Should see: "✅ Admin user created successfully!"

---

## STEP 9: Verify Full Deployment (15 minutes)

### 9.1 Test Login
1. Go to `https://condomanager.vercel.app`
2. Login with admin credentials from Step 8
3. Should see Manager Dashboard

### 9.2 Test Report Flow
1. **Via Telegram**:
   - Send `/report` to bot
   - Complete 5-step flow
   - Should get report ID

2. **Via Web**:
   - Login as owner (create owner user first in dashboard)
   - Go to Owner Dashboard → Submit Report
   - Fill form and submit

3. **Manager Dashboard**:
   - Should see new report
   - Click to acknowledge
   - Create task from report
   - Assign to employee

### 9.3 Test Notifications
- When manager acknowledges report, owner should get Telegram notification
- When task assigned, employee should get notification

---

## Post-Deployment Checklist

- [ ] Backend health check passes: `GET /health`
- [ ] Frontend loads without errors
- [ ] Login works with admin credentials
- [ ] Telegram bot responds to `/start`
- [ ] Telegram `/report` command works
- [ ] Report shows in Manager Dashboard
- [ ] Can create task from report
- [ ] Notifications arrive in Telegram
- [ ] All tables visible in Supabase

---

## Common Issues & Solutions

### Issue: "Database connection failed"
**Solution**: 
- Check DATABASE_URL format matches Supabase URI exactly
- Ensure password doesn't have special characters that need URL encoding
- Try connecting with `psql` locally first

### Issue: "CORS error" in browser
**Solution**:
- Verify CORS_ORIGINS in Render includes your Vercel URL
- Check FRONTEND_URL matches exactly (no trailing slash difference)
- Redeploy backend after changing env vars

### Issue: "Telegram webhook not working"
**Solution**:
- Verify backend URL uses HTTPS (Telegram requires SSL)
- Check webhook URL with `getWebhookInfo` API call
- Look at Render logs for webhook handler errors
- Ensure `/telegram/webhook` endpoint is not blocked by auth middleware

### Issue: "Migrations failed"
**Solution**:
- Check Supabase SQL Editor: run `CREATE EXTENSION IF NOT EXISTS "uuid-ossp";`
- Verify DATABASE_URL is correct
- Check Render logs for specific migration error
- Try running one migration at a time: `alembic upgrade +1`

---

## Next Steps After Deployment

### Week 1: Monitoring
- Check Render logs daily
- Monitor Supabase database usage (free tier: 500MB)
- Test all user flows (owner, employee, manager)

### Week 2: Enhancements
- Set up custom domain (if desired)
- Configure email sending (SendGrid)
- Add real building/apartment data

### Month 2: Scaling (if needed)
- Upgrade Render to paid tier ($7/mo) - removes sleep timeout
- Upgrade Supabase if approaching 500MB
- Add Cloudinary for image uploads

---

## Cost Summary (Free Tier)

| Service | Free Tier | CondoManager Usage |
|---------|-----------|-------------------|
| Supabase | 500MB storage, 2GB bandwidth | ✅ Sufficient for small building |
| Render | 750 hrs/month, sleeps after 15min | ✅ Good for low traffic |
| Vercel | Unlimited deploys, 100GB bandwidth | ✅ Unlimited |
| Telegram | Unlimited messages | ✅ Unlimited |
| **TOTAL** | | **$0/month** |

---

## Support Resources

- **Supabase**: https://supabase.com/docs
- **Render**: https://render.com/docs
- **Vercel**: https://vercel.com/docs
- **CondoManager Issues**: https://github.com/tabgab/CondoManager/issues

---

## Quick Reference: All Your URLs

Fill this in as you deploy:

| Service | URL | Status |
|---------|-----|--------|
| Supabase Project | https://app.supabase.com/project/xxxxxx | ✅ Created |
| Backend (Render) | https://condomanager-backend.onrender.com | ⬜ Deploy |
| Frontend (Vercel) | https://condomanager.vercel.app | ⬜ Deploy |
| Telegram Bot | @condomanagertest_bot | ✅ Ready |

---

**Start with Step 1 now!** 🚀
