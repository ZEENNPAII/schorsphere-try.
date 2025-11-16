# Vercel Database Setup - Quick Guide

## ❌ Why SQLite Doesn't Work on Vercel

Vercel is a **serverless platform** with a **read-only filesystem**. SQLite needs to write files, which is not possible on Vercel.

## ✅ Databases That Work on Vercel

### 1. **Vercel Postgres** (Recommended - Easiest) ⭐
- **Native Vercel integration**
- **Free tier**: 256 MB storage, 60 hours compute/month
- **Setup**: 2 minutes
- **Best for**: Most applications

### 2. **External PostgreSQL** (Supabase, Neon, Railway, etc.)
- **Free tiers available**
- **Setup**: 5-10 minutes
- **Best for**: If you need more features

### 3. **External MySQL** (PlanetScale, Railway, etc.)
- **Free tiers available**
- **Setup**: 5-10 minutes
- **Best for**: If you prefer MySQL

---

## 🚀 Quick Setup: Vercel Postgres (Recommended)

### Step 1: Create Vercel Postgres Database

1. Go to [vercel.com](https://vercel.com) → Your Project
2. Click **"Storage"** tab
3. Click **"Create Database"**
4. Select **"Postgres"**
5. Name it (e.g., `scholarsphere-db`)
6. Select region (closest to your users)
7. Click **"Create"**

### Step 2: Get Connection String

1. Click on your database
2. Go to **"Settings"** tab
3. Find **"Connection String"** section
4. Click **"View Connection String"**
5. Copy the `POSTGRES_URL` (it looks like: `postgres://user:pass@host:port/dbname`)

### Step 3: Add Environment Variables

1. Go to Project → **Settings** → **Environment Variables**
2. Add these variables:

   **Variable 1:**
   - **Key:** `DATABASE_URL`
   - **Value:** (paste the POSTGRES_URL you copied)
   - ✅ Check: Production, Preview, Development

   **Variable 2:**
   - **Key:** `SECRET_KEY`
   - **Value:** (generate a random string - see below)
   - ✅ Check: Production, Preview, Development

3. Click **"Save"**

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 4: Deploy

1. **Push to GitHub** (if connected) or **Redeploy** on Vercel
2. The app will **automatically create tables** on first run!

---

## 🔧 Alternative: Supabase (Free PostgreSQL)

### Step 1: Create Supabase Account

1. Go to [supabase.com](https://supabase.com)
2. Sign up (free)
3. Click **"New Project"**

### Step 2: Create Project

1. Choose organization
2. Name: `scholarsphere`
3. Database password: (create a strong password)
4. Region: (choose closest)
5. Click **"Create new project"**
6. Wait ~2 minutes for setup

### Step 3: Get Connection String

1. Go to **Project Settings** → **Database**
2. Under **"Connection string"**, select **"URI"**
3. Copy the connection string
4. It looks like: `postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres`

### Step 4: Add to Vercel

1. Go to Vercel → Your Project → **Settings** → **Environment Variables**
2. Add:
   - **Key:** `DATABASE_URL`
   - **Value:** (paste connection string from Supabase)
   - ✅ Check all environments
3. Click **"Save"**

### Step 5: Deploy

1. Redeploy your Vercel project
2. Tables will be created automatically!

---

## 🔧 Alternative: PlanetScale (Free MySQL)

### Step 1: Create Account

1. Go to [planetscale.com](https://planetscale.com)
2. Sign up (free)
3. Click **"Create database"**

### Step 2: Create Database

1. Name: `scholarsphere`
2. Region: (choose closest)
3. Click **"Create database"**
4. Select **"Development"** branch

### Step 3: Get Connection String

1. Click **"Connect"** button
2. Select **"Python"** → **"Prisma"**
3. Copy the connection string
4. It looks like: `mysql://user:pass@host/database?sslaccept=strict`

### Step 4: Add to Vercel

1. Go to Vercel → Your Project → **Settings** → **Environment Variables**
2. Add:
   - **Key:** `DATABASE_URL`
   - **Value:** (paste connection string)
   - ✅ Check all environments
3. Click **"Save"**

### Step 5: Deploy

1. Redeploy your Vercel project
2. Tables will be created automatically!

---

## ✅ Verify It Works

1. Visit your Vercel app URL
2. Try to **create an account** - should work!
3. Try to **login** - should work!
4. **Default admin:**
   - Email: `admin@scholarsphere.com`
   - Password: `admin123`

---

## 🆘 Troubleshooting

### Error: "relation does not exist" or "table does not exist"
**Solution:** Tables haven't been created yet. The app creates them automatically on first run. If it doesn't work:
1. Check Vercel logs for errors
2. Make sure `DATABASE_URL` is set correctly
3. Try accessing your app again (tables should be created)

### Error: "connection refused" or "timeout"
**Solution:**
- Check your `DATABASE_URL` is correct
- Make sure database is in the same region
- Verify environment variables are set in Vercel

### Error: "SSL connection required"
**Solution:** The app automatically handles SSL. If you see this:
- Make sure connection string includes SSL parameters
- For Supabase/Neon: SSL is automatic
- For PlanetScale: Add `?sslaccept=strict` to connection string

### Error: "too many connections"
**Solution:**
- Your database has connection limits
- The app uses connection pooling
- Consider upgrading your database plan

---

## 📋 Checklist

- [ ] Created database (Vercel Postgres, Supabase, or PlanetScale)
- [ ] Got connection string
- [ ] Added `DATABASE_URL` to Vercel environment variables
- [ ] Added `SECRET_KEY` to Vercel environment variables
- [ ] Redeployed application
- [ ] Tested account creation
- [ ] Tested login

---

## 💡 Recommended: Vercel Postgres

**Why Vercel Postgres?**
- ✅ Native integration (easiest setup)
- ✅ Automatic environment variables
- ✅ Free tier is generous
- ✅ No extra accounts needed
- ✅ Works seamlessly with Vercel

**Get started:** Just follow "Quick Setup: Vercel Postgres" above!

---

**Need more help?** Check Vercel logs: Go to your project → Deployments → Click on deployment → Functions tab

