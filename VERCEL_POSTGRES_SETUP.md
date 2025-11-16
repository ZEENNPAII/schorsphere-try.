# Complete Vercel PostgreSQL Setup Guide

This guide will help you set up PostgreSQL database on Vercel and configure your ScholarSphere application.

## Step 1: Create Vercel Postgres Database

### Option A: Via Vercel Dashboard (Recommended)

1. **Go to Vercel Dashboard**
   - Visit [vercel.com](https://vercel.com) and log in
   - Select your project (or create a new one)

2. **Create Postgres Database**
   - Click on your project
   - Go to the **"Storage"** tab
   - Click **"Create Database"**
   - Select **"Postgres"**
   - Choose a name (e.g., `scholarsphere-db`)
   - Select a region (choose closest to your users)
   - Click **"Create"**

3. **Get Connection String**
   - After creation, click on your database
   - Go to **"Settings"** tab
   - Find **"Connection String"** section
   - Click **"View Connection String"**
   - Copy the `POSTGRES_URL` (it looks like: `postgres://user:pass@host:port/dbname`)

### Option B: Via Vercel CLI

```bash
# Install Vercel CLI if you haven't
npm i -g vercel

# Login to Vercel
vercel login

# Link your project
vercel link

# Create Postgres database
vercel addons create postgres

# Get connection string
vercel env pull
```

## Step 2: Add Environment Variables to Vercel

1. **In Vercel Dashboard**
   - Go to your project → **Settings** → **Environment Variables**

2. **Add these variables:**

   ```
   DATABASE_URL = (paste the POSTGRES_URL from Step 1)
   SECRET_KEY = (generate a random secret key - see below)
   ```

3. **Generate SECRET_KEY:**
   ```bash
   # On Linux/Mac:
   python -c "import secrets; print(secrets.token_hex(32))"
   
   # On Windows PowerShell:
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

4. **Important Settings:**
   - Make sure to select **Production**, **Preview**, and **Development** environments
   - Click **"Save"**

## Step 3: Set Up Database Tables

You have **3 options** to create the database tables:

### Option A: Automatic (Recommended - Easiest)

The app will automatically create tables on first run. Just deploy and it works!

1. **Deploy your app to Vercel**
2. **Visit your app** - tables will be created automatically
3. **Done!**

### Option B: Using Python Script (Recommended for Initial Setup)

1. **Set DATABASE_URL locally:**
   ```bash
   # On Linux/Mac:
   export DATABASE_URL="postgresql://user:pass@host:port/dbname"
   
   # On Windows:
   set DATABASE_URL=postgresql://user:pass@host:port/dbname
   
   # On Windows PowerShell:
   $env:DATABASE_URL="postgresql://user:pass@host:port/dbname"
   ```

2. **Run setup script:**
   ```bash
   python setup_postgresql.py
   ```

   This will:
   - Create all database tables
   - Create default admin user
   - Verify everything works

### Option C: Manual SQL Script

1. **Connect to your database** using any PostgreSQL client:
   - [pgAdmin](https://www.pgadmin.org/)
   - [DBeaver](https://dbeaver.io/)
   - [TablePlus](https://tableplus.com/)
   - Or Vercel's built-in SQL editor

2. **Run the SQL script:**
   ```bash
   # Using psql command line:
   psql "your-connection-string" < create_postgresql_tables.sql
   
   # Or copy-paste the contents of create_postgresql_tables.sql
   # into your database client's SQL editor
   ```

## Step 4: Verify Setup

1. **Check tables were created:**
   - Connect to your database
   - You should see these tables:
     - `users`
     - `awards`
     - `credentials`
     - `scholarships`
     - `scholarship_applications`
     - `notifications`
     - `schedule`
     - `remarks` (if applicable)
     - `scholarship_application_files` (if applicable)

2. **Check admin user:**
   - Email: `admin@scholarsphere.com`
   - Password: `admin123`
   - **⚠️ Change this password immediately after first login!**

3. **Test your app:**
   - Visit your Vercel deployment
   - Try to create an account
   - Try to login
   - Everything should work!

## Step 5: Deploy to Vercel

1. **Push to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Add PostgreSQL support for Vercel"
   git push
   ```

2. **Vercel will auto-deploy**, or manually deploy:
   ```bash
   vercel --prod
   ```

3. **Check deployment logs:**
   - Go to Vercel Dashboard → Your Project → Deployments
   - Click on the latest deployment
   - Check "Functions" tab for any errors

## Troubleshooting

### Error: "relation does not exist"
**Solution:** Tables haven't been created yet. Run `python setup_postgresql.py` or the SQL script.

### Error: "connection refused" or "timeout"
**Solution:** 
- Check your `DATABASE_URL` is correct
- Make sure database is in the same region
- Check Vercel environment variables are set correctly

### Error: "SSL connection required"
**Solution:** The app automatically handles this, but if you see this error:
- Make sure your connection string includes SSL parameters
- Vercel Postgres automatically uses SSL

### Error: "too many connections"
**Solution:**
- Your database has connection limits
- The app uses connection pooling
- Consider upgrading your database plan if needed

### Tables not creating automatically
**Solution:**
1. Check Vercel logs for errors
2. Manually run: `python setup_postgresql.py` with DATABASE_URL set
3. Or run the SQL script manually

## Database Schema Overview

Your database will have these tables:

- **users** - All users (students, providers, admins)
- **awards** - Student awards/achievements
- **credentials** - Student documents/credentials
- **scholarships** - Scholarship listings
- **scholarship_applications** - Student applications
- **notifications** - User notifications
- **schedule** - Interview/appointment schedules
- **remarks** - Provider remarks on applications
- **scholarship_application_files** - Files attached to applications

## Default Admin Account

After setup, you can login with:
- **Email:** `admin@scholarsphere.com`
- **Password:** `admin123`

**⚠️ IMPORTANT:** Change this password immediately after first login!

## Next Steps

1. ✅ Database is set up
2. ✅ Tables are created
3. ✅ Admin user exists
4. 🔄 **Change admin password**
5. 🔄 **Test account creation**
6. 🔄 **Test password reset**
7. 🔄 **Add your first scholarship provider**
8. 🔄 **Start using the application!**

## Need Help?

- Check Vercel logs: `vercel logs` or in Dashboard
- Check database connection in Vercel Storage dashboard
- Test connection string locally first
- Make sure all environment variables are set correctly

---

**You're all set!** Your ScholarSphere application is now ready to use with PostgreSQL on Vercel! 🎉

