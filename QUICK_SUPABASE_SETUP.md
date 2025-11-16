# Quick Supabase Setup (5 Minutes)

## 🚀 Fastest Way to Connect Supabase

### Step 1: Create Supabase Project (2 min)

1. Go to [supabase.com](https://supabase.com) → **Sign Up** (free)
2. Click **"New Project"**
3. Fill in:
   - Name: `scholarsphere`
   - Password: **SAVE THIS PASSWORD!** (you'll need it)
   - Region: Choose closest to you
4. Click **"Create new project"**
5. Wait 2-3 minutes

### Step 2: Get Connection String (1 min)

1. In Supabase Dashboard → **Settings** → **Database**
2. Scroll to **"Connection string"**
3. Click **"URI"** tab
4. Copy the connection string
5. **Replace `[YOUR-PASSWORD]`** with your actual password
6. Example:
   ```
   postgresql://postgres:MyPassword123@db.xxxxx.supabase.co:5432/postgres
   ```

### Step 3: Add to Vercel (1 min)

1. Go to [vercel.com](https://vercel.com) → Your Project
2. **Settings** → **Environment Variables**
3. Click **"Add New"**
4. Add:
   - **Key:** `DATABASE_URL`
   - **Value:** (paste connection string from Step 2)
   - ✅ Check: Production, Preview, Development
5. Click **"Save"**

### Step 4: Deploy (1 min)

1. Go to **Deployments** tab
2. Click **"Redeploy"** on latest deployment
3. **Done!** 🎉

---

## ✅ Test It Works

1. Visit your Vercel app
2. Try to **create an account** - should work!
3. Check Supabase → **Table Editor** → You should see `users` table with your account

---

## 🆘 Troubleshooting

**Tables not created?**
- The app creates them automatically on first run
- If not, check Vercel logs for errors

**Connection error?**
- Make sure you replaced `[YOUR-PASSWORD]` in connection string
- Verify `DATABASE_URL` is set in Vercel

**Still having issues?**
- See full guide: `SUPABASE_SETUP_GUIDE.md`

---

**That's it!** Your app is now connected to Supabase! 🚀

