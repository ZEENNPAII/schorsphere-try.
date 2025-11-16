# Fix: Use Supabase Connection Pooler

## Important: Use Port 6543 for Serverless Functions!

Supabase provides a **connection pooler** specifically for serverless functions. You MUST use port **6543** instead of **5432** when connecting from Vercel.

## Your Current Connection String (WRONG for Vercel)

```
postgresql://postgres:[Cc09331685853!!]@db.hnlypdmzvmdehrzunqke.supabase.co:5432/postgres
```

## Correct Connection String for Vercel (USE THIS!)

```
postgresql://postgres:[Cc09331685853!!]@db.hnlypdmzvmdehrzunqke.supabase.co:6543/postgres?pgbouncer=true
```

**Changes:**
- Port changed from `5432` → `6543` (connection pooler)
- Added `?pgbouncer=true` parameter

## How to Fix

### Step 1: Update Vercel Environment Variable

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Find `DATABASE_URL`
3. **Update the value** to:
   ```
   postgresql://postgres:[Cc09331685853!!]@db.hnlypdmzvmdehrzunqke.supabase.co:6543/postgres?pgbouncer=true
   ```
4. Click **"Save"**

### Step 2: Redeploy

1. Go to Deployments tab
2. Click "Redeploy" on latest deployment
3. Or push a new commit to trigger auto-deploy

### Step 3: Test

1. Visit your app
2. Should work now! ✅

---

## Why This Matters

- **Port 5432**: Direct database connection (limited connections)
- **Port 6543**: Connection pooler (unlimited connections for serverless)

Serverless functions need the pooler to avoid connection limit errors!

---

## Alternative: Get Pooler Connection String from Supabase

1. Go to Supabase Dashboard → Your Project
2. Settings → Database
3. Scroll to **"Connection string"**
4. Select **"Connection pooling"** tab
5. Copy the connection string (it will use port 6543)
6. Use that in Vercel!

---

**This should fix your 500 error!** 🎉

