# Vercel Database Setup Guide

## Why SQLite Doesn't Work on Vercel

Vercel is a **serverless platform** where:
- The filesystem is **read-only**
- Each function invocation may run on a different server
- SQLite files cannot persist or be written to

**Solution**: Use a cloud database service!

## Recommended Database Options for Vercel

### Option 1: Vercel Postgres (Recommended - Easiest)
- **Free tier**: 256 MB storage, 60 hours compute/month
- **Native Vercel integration**
- **Setup time**: 5 minutes

### Option 2: Supabase (PostgreSQL)
- **Free tier**: 500 MB database, unlimited API requests
- **Great for development**
- **Setup time**: 10 minutes

### Option 3: PlanetScale (MySQL)
- **Free tier**: 5 GB storage, 1 billion row reads/month
- **MySQL-compatible** (works with your existing PyMySQL)
- **Setup time**: 10 minutes

### Option 4: Neon (PostgreSQL)
- **Free tier**: 3 GB storage
- **Serverless PostgreSQL**
- **Setup time**: 10 minutes

---

## Setup Instructions

### Option 1: Vercel Postgres (Easiest)

1. **Install Vercel Postgres**:
   ```bash
   vercel addons create postgres
   ```

2. **Or via Vercel Dashboard**:
   - Go to your project on Vercel
   - Click "Storage" tab
   - Click "Create Database" → Select "Postgres"
   - Choose a name and region

3. **Get Connection String**:
   - In Vercel Dashboard → Your Project → Storage → Postgres
   - Click "View Connection String"
   - Copy the `POSTGRES_URL`

4. **Add to Vercel Environment Variables**:
   - Go to Project Settings → Environment Variables
   - Add: `DATABASE_URL` = `POSTGRES_URL` (from step 3)
   - Deploy again

5. **Initialize Database**:
   - The app will auto-create tables on first run
   - Or run: `python init_database.py` locally with the connection string

---

### Option 2: Supabase (PostgreSQL)

1. **Create Account**: Go to [supabase.com](https://supabase.com)

2. **Create New Project**:
   - Click "New Project"
   - Choose organization, name, database password
   - Select region closest to you
   - Wait for project to be created (~2 minutes)

3. **Get Connection String**:
   - Go to Project Settings → Database
   - Under "Connection string", select "URI"
   - Copy the connection string
   - Format: `postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres`

4. **Add to Vercel Environment Variables**:
   - Go to Vercel Dashboard → Your Project → Settings → Environment Variables
   - Add: `DATABASE_URL` = (connection string from step 3)
   - Deploy again

5. **Initialize Database**:
   - Run the app - tables will be created automatically
   - Or use Supabase SQL Editor to run migrations

---

### Option 3: PlanetScale (MySQL)

1. **Create Account**: Go to [planetscale.com](https://planetscale.com)

2. **Create Database**:
   - Click "Create database"
   - Choose name and region
   - Select "Development" branch

3. **Get Connection String**:
   - Go to your database → "Connect"
   - Select "Python" → "Prisma"
   - Copy the connection string
   - Format: `mysql://[USER]:[PASSWORD]@[HOST]/[DATABASE]?sslaccept=strict`

4. **Add to Vercel Environment Variables**:
   - Go to Vercel Dashboard → Your Project → Settings → Environment Variables
   - Add: `DATABASE_URL` = (connection string from step 3)
   - Deploy again

5. **Initialize Database**:
   - Tables will be created automatically on first run

---

## Environment Variables Setup

### In Vercel Dashboard:

1. Go to your project → **Settings** → **Environment Variables**

2. Add these variables:

   ```
   DATABASE_URL=postgresql://user:password@host:port/database
   SECRET_KEY=your-secret-key-here-change-this
   ```

3. **Important**: 
   - Make sure `DATABASE_URL` is set for **Production**, **Preview**, and **Development**
   - Click "Save" and **redeploy** your application

---

## Testing Database Connection

### Local Testing with Cloud Database:

1. **Create `.env` file** (don't commit this):
   ```env
   DATABASE_URL=postgresql://user:password@host:port/database
   SECRET_KEY=your-secret-key
   ```

2. **Run locally**:
   ```bash
   python app.py
   ```

3. **Initialize database**:
   ```bash
   python init_database.py
   ```

---

## Database Initialization

The app will automatically create tables when it starts. But you can also initialize manually:

### Using Python Script:
```bash
python init_database.py
```

### Or manually via SQL:
Connect to your database and run the table creation SQL (see `app.py` models).

---

## Troubleshooting

### Error: "relation does not exist"
- **Solution**: Tables haven't been created yet. Run `python init_database.py` or restart the app.

### Error: "connection refused"
- **Solution**: Check your `DATABASE_URL` is correct and the database is accessible.

### Error: "SSL connection required"
- **Solution**: Add `?sslmode=require` to PostgreSQL connection string, or use PlanetScale which handles SSL automatically.

### Error: "too many connections"
- **Solution**: Your database has connection limits. The app uses connection pooling, but you may need to upgrade your database plan.

---

## Quick Start Checklist

- [ ] Choose a database provider (Vercel Postgres recommended)
- [ ] Create database and get connection string
- [ ] Add `DATABASE_URL` to Vercel environment variables
- [ ] Add `SECRET_KEY` to Vercel environment variables
- [ ] Redeploy your Vercel application
- [ ] Test account creation and password reset
- [ ] Initialize database tables (if needed)

---

## Cost Comparison

| Provider | Free Tier | Paid Plans Start At |
|----------|-----------|---------------------|
| Vercel Postgres | 256 MB, 60 hrs/month | $20/month |
| Supabase | 500 MB | $25/month |
| PlanetScale | 5 GB | $29/month |
| Neon | 3 GB | $19/month |

**For development/testing**: All free tiers are sufficient!

---

## Need Help?

- Check Vercel logs: `vercel logs`
- Check database connection in your provider's dashboard
- Test connection string locally first
- Make sure environment variables are set correctly

