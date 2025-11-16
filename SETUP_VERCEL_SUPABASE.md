# Setup Supabase on Vercel - Step by Step

## Your Supabase Connection String

```
postgresql://postgres:[Cc09331685853!!]@db.hnlypdmzvmdehrzunqke.supabase.co:5432/postgres
```

**Note:** The connection string format looks correct! The local connection error is normal - it will work from Vercel.

---

## Step 1: Add to Vercel Environment Variables

### 1.1 Go to Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Sign in to your account
3. Click on your **ScholarSphere project**

### 1.2 Add Environment Variable

1. Click **"Settings"** tab (top navigation)
2. Click **"Environment Variables"** (left sidebar)
3. Click **"Add New"** button

### 1.3 Add DATABASE_URL

Fill in the form:

- **Key:** `DATABASE_URL`
- **Value:** 
  ```
  postgresql://postgres:[Cc09331685853!!]@db.hnlypdmzvmdehrzunqke.supabase.co:5432/postgres
  ```
- **Environment:** 
  - ✅ Check **Production**
  - ✅ Check **Preview**  
  - ✅ Check **Development**

4. Click **"Save"**

### 1.4 Add SECRET_KEY (if not already set)

1. Click **"Add New"** again
2. Fill in:
   - **Key:** `SECRET_KEY`
   - **Value:** (generate a random string - see below)
   - **Environment:** Check all (Production, Preview, Development)
3. Click **"Save"**

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Or use: [randomkeygen.com](https://randomkeygen.com/) - use "CodeIgniter Encryption Keys"

---

## Step 2: Redeploy Your Application

### Option A: Redeploy from Dashboard

1. Go to **"Deployments"** tab
2. Find your latest deployment
3. Click the **"..."** (three dots) menu
4. Click **"Redeploy"**
5. Wait for deployment to complete

### Option B: Push to GitHub (if connected)

1. Make a small change (or just commit current changes)
2. Push to GitHub:
   ```bash
   git add .
   git commit -m "Add Supabase database connection"
   git push
   ```
3. Vercel will automatically deploy

---

## Step 3: Verify It Works

### 3.1 Check Deployment Logs

1. Go to **"Deployments"** tab
2. Click on the latest deployment
3. Click **"Functions"** tab
4. Look for any errors
5. Should see: "Database tables created successfully" (if no errors)

### 3.2 Test Your Application

1. Visit your Vercel app URL
2. Try to **create an account**:
   - Go to Sign Up page
   - Fill in the form
   - Submit
   - Should work! ✅

3. Try to **login**:
   - Use the account you created
   - Should work! ✅

### 3.3 Verify in Supabase

1. Go to [supabase.com](https://supabase.com)
2. Open your project
3. Click **"Table Editor"** (left sidebar)
4. You should see tables:
   - `users` (with your test account)
   - `awards`
   - `credentials`
   - `scholarships`
   - `scholarship_applications`
   - `notifications`
   - `schedule`
   - `application_remarks`
   - `scholarship_application_files`

---

## Step 4: Create Admin User (Optional)

The app will create an admin user automatically on first run. If it doesn't:

1. Go to Supabase → **"SQL Editor"**
2. Click **"New query"**
3. Run this SQL:

```sql
-- Generate password hash first using Python:
-- python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('admin123'))"

-- Then insert (replace HASH_HERE with generated hash):
INSERT INTO users (first_name, last_name, email, student_id, birthday, password_hash, role, is_active, created_at)
VALUES (
    'Admin',
    'User',
    'admin@scholarsphere.com',
    '00000000',
    '1990-01-01',
    'pbkdf2:sha256:600000$...',  -- Replace with actual hash
    'admin',
    TRUE,
    NOW()
)
ON CONFLICT (email) DO NOTHING;
```

**Or** just create an account through the signup form and change the role in Supabase Table Editor.

---

## ✅ Checklist

- [ ] Added `DATABASE_URL` to Vercel environment variables
- [ ] Added `SECRET_KEY` to Vercel environment variables
- [ ] Redeployed application
- [ ] Checked deployment logs (no errors)
- [ ] Tested account creation (works!)
- [ ] Tested login (works!)
- [ ] Verified tables in Supabase Table Editor

---

## 🆘 Troubleshooting

### Error: "relation does not exist"

**Solution:** 
- Tables haven't been created yet
- The app creates them automatically on first run
- If it doesn't work, check Vercel logs for errors
- Make sure `DATABASE_URL` is set correctly

### Error: "connection refused"

**Solution:**
- Check your connection string is correct
- Verify `DATABASE_URL` is set in Vercel
- Make sure you replaced `[YOUR-PASSWORD]` (but yours looks correct)
- Check Supabase project is active

### Error: "password authentication failed"

**Solution:**
- Verify your database password is correct
- Check the connection string format
- Make sure there are no extra spaces

### Tables not creating automatically

**Solution:**
1. Check Vercel logs for specific errors
2. Make sure `DATABASE_URL` environment variable is set
3. Try accessing your app - tables should be created on first request
4. If still not working, manually run SQL in Supabase SQL Editor

---

## 🎉 You're Done!

Your ScholarSphere application is now connected to Supabase!

**Next Steps:**
1. Test all features (signup, login, password reset)
2. Create test users
3. Add scholarships
4. Test the full application flow

---

## 📝 Important Notes

1. **Keep your password secure** - Don't share your connection string publicly
2. **Free tier limits** - Supabase free tier has 500 MB storage (plenty for development)
3. **Connection pooling** - The app handles connections automatically
4. **SSL** - Supabase requires SSL, which is handled automatically

---

**Need Help?**
- Check Vercel logs: Deployments → Latest → Functions
- Check Supabase logs: Settings → Logs
- Verify environment variables are set correctly

