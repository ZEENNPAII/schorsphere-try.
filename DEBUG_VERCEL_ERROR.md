# Debug Vercel 500 Error

## Quick Debugging Steps

### 1. Check Vercel Logs

1. Go to Vercel Dashboard → Your Project
2. Click **"Deployments"** tab
3. Click on the **latest deployment**
4. Click **"Functions"** tab
5. Look for error messages

### 2. Test Health Endpoint

Visit: `https://your-app.vercel.app/health`

This will show:
- If the app is running
- If database is configured
- Any errors

### 3. Check Environment Variables

In Vercel Dashboard → Settings → Environment Variables:

**Required:**
- `DATABASE_URL` = `postgresql://postgres:[Cc09331685853!!]@db.hnlypdmzvmdehrzunqke.supabase.co:5432/postgres`
- `SECRET_KEY` = (your secret key)

**Make sure:**
- ✅ Both are set for Production, Preview, and Development
- ✅ No extra spaces in values
- ✅ Connection string is correct

### 4. Common Error Messages

#### "ModuleNotFoundError"
**Solution:** Check `requirements.txt` has all dependencies

#### "Database connection failed"
**Solution:** 
- Verify `DATABASE_URL` is correct
- Check Supabase project is active
- Test connection string format

#### "Table does not exist"
**Solution:** Tables are created automatically on first request. Wait a moment and try again.

#### "Import error"
**Solution:** Check if all Python files are in the repository

### 5. Test Locally First

```bash
# Set environment variable
export DATABASE_URL="postgresql://postgres:[Cc09331685853!!]@db.hnlypdmzvmdehrzunqke.supabase.co:5432/postgres"

# Run app
python app.py
```

If it works locally but not on Vercel, it's likely an environment variable issue.

### 6. Check Vercel Build Logs

1. Go to Deployments → Latest
2. Click on the deployment
3. Check **"Build Logs"** tab
4. Look for Python errors during build

### 7. Verify File Structure

Make sure these files exist:
- `api/index.py` ✅
- `app.py` ✅
- `vercel.json` ✅
- `requirements.txt` ✅

### 8. Test Connection String

Your connection string:
```
postgresql://postgres:[Cc09331685853!!]@db.hnlypdmzvmdehrzunqke.supabase.co:5432/postgres
```

**Verify:**
- ✅ Starts with `postgresql://` (not `postgres://`)
- ✅ Password is correct: `[Cc09331685853!!]`
- ✅ Host is correct: `db.hnlypdmzvmdehrzunqke.supabase.co`
- ✅ Port is `5432`
- ✅ Database is `postgres`

---

## What I Fixed

1. ✅ Improved error handling in `api/index.py`
2. ✅ Added connection test before creating tables
3. ✅ Made database initialization safer
4. ✅ Added health check endpoint (`/health`)
5. ✅ Better error messages

---

## Next Steps

1. **Redeploy** on Vercel (should auto-deploy from GitHub)
2. **Check logs** after deployment
3. **Test** `/health` endpoint
4. **Test** your main app URL

If still getting errors, check the specific error message in Vercel logs and share it!

