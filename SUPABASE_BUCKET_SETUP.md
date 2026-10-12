# 📦 Supabase Storage Bucket Setup

## Why You Need This

The resume upload feature requires a Supabase Storage bucket called **"resumes"** to store uploaded PDF files. Without it, uploads will work but files won't be permanently stored.

---

## ✅ Quick Setup (5 minutes)

### Step 1: Go to Supabase Dashboard
1. Open: https://supabase.com/dashboard
2. Login with your account
3. Select your project: **awysaiowibawcsmngoch**

### Step 2: Create Storage Bucket
1. Click on **Storage** in left sidebar
2. Click **"New bucket"** or **"Create bucket"**
3. Fill in the details:
   - **Name:** `resumes`
   - **Public bucket:** ✅ Check this (so URLs work)
   - **File size limit:** 5MB (recommended)
   - **Allowed MIME types:** application/pdf, application/vnd.openxmlformats-officedocument.wordprocessingml.document

### Step 3: Set Bucket Policies
1. Click on the **"resumes"** bucket
2. Go to **"Policies"** tab
3. Add these policies:

**Policy 1: Allow Uploads (INSERT)**
```sql
CREATE POLICY "Allow authenticated users to upload resumes"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'resumes' AND
  (storage.foldername(name))[1] = auth.uid()::text
);
```

**Policy 2: Allow Read (SELECT)**
```sql
CREATE POLICY "Allow users to read their own resumes"
ON storage.objects FOR SELECT
TO authenticated, anon
USING (bucket_id = 'resumes');
```

**Policy 3: Allow Delete**
```sql
CREATE POLICY "Allow users to delete their own resumes"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'resumes' AND
  (storage.foldername(name))[1] = auth.uid()::text
);
```

### Step 4: Verify Setup
1. Go back to Storage
2. You should see **"resumes"** bucket listed
3. Status should be **"Public"**

---

## 🧪 Test the Setup

### Option 1: Test via UI
1. Go to http://localhost:3000
2. Login
3. Navigate to Resume Analyzer
4. Upload a PDF
5. Should work without errors!

### Option 2: Test via API
```bash
curl -X POST http://localhost:8000/api/v1/resumes/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@D:/Main details/Anagesh_Resume.pdf" \
  -F "title=My Resume"
```

---

## ⚠️ Troubleshooting

### Error: "Bucket not found"
- **Solution:** Create the bucket as described in Step 2

### Error: "Permission denied"
- **Solution:** Add the policies from Step 3

### Error: "File size too large"
- **Solution:** Check file is under 5MB
- Increase bucket limit in Supabase settings

### Error: "Invalid file type"
- **Solution:** Only PDF and DOCX supported
- Check MIME type configuration

---

## 🔒 Security Notes

### Current Setup:
- ✅ Users can only upload to their own folder (`user_id/filename`)
- ✅ Users can only delete their own files
- ✅ Public read access (for displaying resumes)
- ✅ 5MB file size limit

### Production Recommendations:
- 🔐 Add virus scanning
- 🔐 Add file type validation
- 🔐 Enable versioning
- 🔐 Set up automatic cleanup for old files
- 🔐 Add rate limiting

---

## 📁 Bucket Structure

Files will be stored like this:
```
resumes/
├── user-uuid-1/
│   ├── Anagesh_Resume.pdf
│   └── Updated_Resume.pdf
├── user-uuid-2/
│   └── Resume_2024.pdf
└── user-uuid-3/
    └── MyResume.pdf
```

Each user gets their own folder (based on UUID).

---

## 🚀 Alternative: Local Storage (Development Only)

If you don't want to set up Supabase storage right now, the app will:
1. Store files with placeholder URLs (`local://user-id/filename`)
2. Resume analysis will still work
3. Files won't be permanently stored
4. Perfect for testing without Supabase setup

**To enable this:** Just don't create the bucket! The error handler will catch it.

---

## ✅ Verification Checklist

After setup, verify:
- [ ] Bucket "resumes" exists
- [ ] Bucket is marked as "Public"
- [ ] INSERT policy exists
- [ ] SELECT policy exists  
- [ ] DELETE policy exists
- [ ] Test upload works
- [ ] File appears in Storage browser

---

## 📞 Need Help?

If you encounter issues:
1. Check Supabase project status
2. Verify service role key in backend/.env
3. Check browser console for errors
4. Share error message for debugging

---

**Status:** Optional setup - app works without it, but files won't persist
**Time to complete:** 5 minutes
**Difficulty:** Easy
