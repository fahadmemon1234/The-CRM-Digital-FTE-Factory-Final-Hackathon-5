# Hugging Face Spaces - Frontend Deployment

## Option 1: Static Export (Recommended for HF)

### Step 1: Build with static export
```bash
cd D:\GIAIC\Hackathon 5\frontend
npm run build
```

### Step 2: Upload 'out' folder to HF Spaces
```bash
# Copy the 'out' folder to your HF Space
xcopy /E /I /Y out D:\GIAIC\AI-Powered-Customer-Success-FTE\public\

# Or use Git
cd D:\GIAIC\AI-Powered-Customer-Success-FTE
git add public/
git commit -m "Add frontend build"
git push origin main
```

## Option 2: Use Vercel (Better for Next.js)

### Fix Vercel Project Settings:

1. Go to: https://vercel.com/fahadmemon1234s-projects/crm_digital_factory/settings
2. **Root Directory**: Set to `frontend`
3. **Build Command**: `npm run build`
4. **Output Directory**: `.next`
5. Save settings

### Then deploy:
```bash
cd D:\GIAIC\Hackathon 5\frontend
vercel deploy --prod
```

## Quick Fix for Current Error:

The error shows Vercel is looking for `frontend/frontend` folder.

**Fix in Vercel Dashboard:**
1. Visit: https://vercel.com/fahadmemon1234s-projects/crm_digital_factory/settings
2. Find "Root Directory" setting
3. Clear it (make it empty) OR set to `frontend`
4. Save
5. Redeploy

## Manual Deploy Steps:

```bash
# 1. Navigate to frontend
cd D:\GIAIC\Hackathon 5\frontend

# 2. Build the project
npm run build

# 3. Deploy to Vercel
vercel --prod

# OR deploy to Hugging Face
# Copy these folders to HF Space:
# - .next/
# - public/
# - package.json
# - next.config.ts
# - vercel.json
```
