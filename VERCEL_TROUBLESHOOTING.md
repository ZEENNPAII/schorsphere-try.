# Vercel 500 Error - Complete Troubleshooting Guide

## 🔍 Step 1: Check What Error You're Getting

### Test These Endpoints:

1. **Test Endpoint (No Database Required):**
   ```
   https://your-app.vercel.app/test
   ```
   - If this works → App is loading, issue is with database/routes
   - If this fails → App import is failing

2. **Health Check:**
   ```
   https://your-app.vercel.app/health
   ```
   - Shows if database is configured
   - Shows app status

3. **Check Vercel Logs:**
   - Go to Vercel Dashboard → Your Project → Deployments
   - Click latest deployment → **"Functions"** tab
   - Look for error messages

---

## 🔧 Step 2: Most Common Fix - Supabase Connection Pooler

### ⚠️ CRITICAL: Use Port 6543, NOT 5432!

Your connection string should be:
```
postgresql://postgres:[Cc09331685853!!]@db.hnlypdmzvmdehrzunqke.supabase.co:6543/postgres?pgbouncer=true
```

**NOT:**
```
postgresql://postgres:[Cc09331685853!!]@db.hnlypdmzvmdehrzunqke.supabase.co:5432/postgres
```

### How to Fix:

1. Go to **Vercel Dashboard** → Your Project → **Settings** → **Environment Variables**
2. Find `DATABASE_URL`
3. **Change port from 5432 to 6543**
4. **Add `?pgbouncer=true`** at the end
5. Click **"Save"**
6. **Redeploy**

---

## 🔧 Step 3: Verify Environment Variables

In Vercel Dashboard → Settings → Environment Variables:

**Required Variables:**
- ✅ `DATABASE_URL` = (your Supabase connection string with port 6543)
- ✅ `SECRET_KEY` = (your secret key)

**Check:**
- ✅ Both are set for **Production**, **Preview**, and **Development**
- ✅ No extra spaces before/after values
- ✅ Connection string is complete and correct

---

## 🔧 Step 4: Check Vercel Build Logs

1. Go to **Deployments** → Latest deployment
2. Click **"Build Logs"** tab
3. Look for:
   - Python errors
   - Missing dependencies
   - Import errors
   - Database connection errors

---

## 🔧 Step 5: Common Errors and Fixes

### Error: "ModuleNotFoundError: No module named 'X'"
**Fix:** Add missing module to `requirements.txt`

### Error: "could not translate host name"
**Fix:** 
- Check connection string format
- Make sure Supabase project is active
- Use port 6543 (pooler) not 5432

### Error: "too many connections"
**Fix:** Use connection pooler (port 6543)

### Error: "relation does not exist"
**Fix:** Tables will be created automatically on first request. Wait and try again.

### Error: "Import error" or "Syntax error"
**Fix:** Check Python files for syntax errors

---

## 🔧 Step 6: Test Connection String

Your connection string format:
```
postgresql://postgres:PASSWORD@HOST:6543/DATABASE?pgbouncer=true
```

**Verify:**
- ✅ Starts with `postgresql://` (not `postgres://`)
- ✅ Password is correct: `[Cc09331685853!!]`
- ✅ Host is correct: `db.hnlypdmzvmdehrzunqke.supabase.co`
- ✅ Port is `6543` (NOT 5432!)
- ✅ Database is `postgres`
- ✅ Has `?pgbouncer=true` parameter

---

## 🔧 Step 7: Get Correct Connection String from Supabase

1. Go to **Supabase Dashboard** → Your Project
2. **Settings** → **Database**
3. Scroll to **"Connection string"**
4. Click **"Connection pooling"** tab (NOT "URI" tab)
5. Copy the connection string
6. It should have port **6543**
7. Use that in Vercel!

---

## ✅ Quick Checklist

- [ ] Updated `DATABASE_URL` to use port **6543** (not 5432)
- [ ] Added `?pgbouncer=true` to connection string
- [ ] `SECRET_KEY` is set in Vercel
- [ ] Both environment variables are set for all environments
- [ ] Redeployed after changing environment variables
- [ ] Tested `/test` endpoint
- [ ] Tested `/health` endpoint
- [ ] Checked Vercel logs for specific errors

---

## 🆘 Still Not Working?

1. **Check Vercel Logs** - Look for the actual error message
2. **Test `/test` endpoint** - Does it work?
3. **Test `/health` endpoint** - What does it show?
4. **Share the error message** from Vercel logs

The error message will tell us exactly what's wrong!

---

## 📝 What I've Added

1. ✅ Better error handling - shows actual error messages
2. ✅ Test endpoint (`/test`) - works without database
3. ✅ Health check (`/health`) - shows app status
4. ✅ Improved error messages - easier to debug
5. ✅ Connection pooler documentation

---

**The most likely fix:** Change port from 5432 to 6543 in your `DATABASE_URL`! 🎯

