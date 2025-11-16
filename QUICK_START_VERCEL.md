# Quick Start: PostgreSQL Setup for Vercel

## 🚀 Fastest Way to Get Started

### Step 1: Create Vercel Postgres (2 minutes)

1. Go to [vercel.com](https://vercel.com) → Your Project
2. Click **"Storage"** tab → **"Create Database"** → **"Postgres"**
3. Name it (e.g., `scholarsphere-db`) and select region
4. Click **"Create"**

### Step 2: Get Connection String (1 minute)

1. Click on your database
2. Go to **"Settings"** → **"Connection String"**
3. Click **"View Connection String"**
4. Copy the `POSTGRES_URL`

### Step 3: Add to Vercel Environment Variables (1 minute)

1. Go to Project → **Settings** → **Environment Variables**
2. Add:
   - **Key:** `DATABASE_URL`
   - **Value:** (paste the POSTGRES_URL)
   - ✅ Check: Production, Preview, Development
3. Click **"Save"**

### Step 4: Deploy & Auto-Setup (Automatic!)

1. **Push to GitHub** or **Redeploy** on Vercel
2. The app will **automatically create all tables** on first run!
3. **Done!** 🎉

---

## 📋 Manual Setup (If Needed)

If automatic setup doesn't work, run this locally:

```bash
# Set your database URL
export DATABASE_URL="postgresql://user:pass@host:port/dbname"

# Run setup script
python setup_postgresql.py
```

---

## ✅ Verify It Works

1. Visit your Vercel app
2. Try to **create an account** - should work!
3. Try to **login** - should work!
4. **Admin login:**
   - Email: `admin@scholarsphere.com`
   - Password: `admin123`

---

## 🆘 Troubleshooting

**Tables not created?**
- Check Vercel logs for errors
- Run `python setup_postgresql.py` manually

**Connection errors?**
- Verify `DATABASE_URL` is set correctly in Vercel
- Make sure database is in same region

**Still having issues?**
- See full guide: `VERCEL_POSTGRES_SETUP.md`

---

**That's it!** Your database is ready! 🚀

