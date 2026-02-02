# 🚀 Deployment Guide - Streamlit Cloud

Complete step-by-step guide for deploying the Olympics Dashboard to Streamlit Community Cloud.

## Prerequisites Checklist

- ✅ GitHub account (lucy.dev256@gmail.com / lucydev256)
- ✅ RapidAPI subscription (BASIC or higher)
- ✅ Streamlit Community Cloud account (free)
- ✅ Project code in GitHub repository

## Step 1: Prepare GitHub Repository

### 1.1 Initialize Git (if not already done)
```bash
cd Olympics_2026
git init
```

### 1.2 Create `.gitignore` ✅ (already created)
This file is already configured to exclude:
- `.env` files (secrets)
- `venv/` directory
- Cache files
- IDE files

### 1.3 Commit and Push to GitHub

```bash
# Stage all files
git add .

# Commit
git commit -m "Initial Olympics 2026 Dashboard commit

- Multi-sport coverage (all 16 winter sports)
- Live dashboard with real-time updates
- Schedule explorer with filters
- Country tracker
- Interactive analytics
- Smart caching strategy"

# Add remote (use your fork)
git remote add origin https://github.com/lucydev256/olympics-2026.git

# Set main branch
git branch -M main

# Push
git push -u origin main
```

### 1.4 Repository Structure Check
Verify on GitHub that these files are present:
- `app.py` (main file)
- `requirements.txt` (dependencies)
- `.streamlit/config.toml` (theme settings)
- `src/` directory with all modules
- `utils/` directory with helpers
- `README.md` and `QUICKSTART.md`

## Step 2: Deploy to Streamlit Cloud

### 2.1 Go to Streamlit Cloud
1. Visit: https://share.streamlit.io/
2. Log in with GitHub account (lucy.dev256@gmail.com)
3. Click "New app" button (top right)

### 2.2 Connect Repository
1. Select:
   - **GitHub account**: lucydev256
   - **Repository**: olympics-2026
   - **Branch**: main
   - **Main file path**: app.py

2. Click "Deploy"

The deployment will take 1-2 minutes. You'll see a progress bar.

## Step 3: Configure Secrets

### 3.1 Access App Settings
Once deployed, click on your app URL (format: `https://share.streamlit.io/lucydev256/olympics-2026/main/app.py`)

In the top right, click the ⋮ (three dots menu) → "Settings"

### 3.2 Add Secret
In the Settings panel on the left:

1. Find **"Secrets"** section
2. Click the **"Edit"** button
3. Add this exact text:
```
RAPIDAPI_KEY=your_actual_api_key_here
```

Where `your_actual_api_key_here` is your RapidAPI key from:
https://rapidapi.com/jxancestral17/api/milano-cortina-2026-olympics-api

4. Click **"Save"**
5. Close the dialog - your app will auto-reload

## Step 4: Verify Deployment

### 4.1 Check App Status
- Look for the green ✅ indicator (should appear within 2-3 minutes)
- If you see a red ❌, check the logs by clicking "Manage app"

### 4.2 Test API Connection
In the deployed app:
1. Look at the bottom of the sidebar
2. Should show "✅ Connected to API"
3. If showing error, verify the RAPIDAPI_KEY secret

### 4.3 Load Data
Click "Live Dashboard" tab:
- Should show today's Olympic events
- If showing "No events," this could be normal if current date is outside Feb 6-22, 2026
- Check the "Schedule" tab to browse events

## Step 5: Configure Custom Domain (Optional)

### 5.1 Custom URL
Go to app settings and add a custom subdomain:
- Example: `olympics-2026-lucy.streamlit.app`

This makes sharing easier!

## Maintenance & Updates

### Auto-Updates
The app automatically redeploys when you push to GitHub's main branch:
```bash
git add .
git commit -m "Update feature or fix"
git push origin main
```

Deployment takes 1-2 minutes.

### Manual Redeploy
In Streamlit Cloud settings: "Reboot app" button

### Monitoring

Check the **"Manage app"** section for:
- Logs (view errors)
- Advanced settings
- Delete app option

## Common Issues & Solutions

### ❌ "API Key not configured"
**Solution:**
1. Go to app settings → Secrets
2. Verify `RAPIDAPI_KEY=` line is exact
3. No extra spaces or line breaks
4. Save and wait 2-3 minutes for reload

### ❌ "Rate limit exceeded"
**Solution:**
1. Check remaining requests in RapidAPI dashboard
2. The BASIC plan has 10,000 requests/month
3. Use the "Clear Cache" button in sidebar
4. Reduce auto-refresh frequency

### ❌ "Module not found" error
**Solution:**
1. Check `requirements.txt` includes all imports
2. Verify all `src/` and `utils/` files are in repository
3. Try reboot app from settings

### ❌ "No events loading"
**Solution:**
1. Verify date is within Feb 6-22, 2026
2. Check API status on RapidAPI dashboard
3. Ensure RAPIDAPI_KEY is correct
4. Look at "Manage app" → Logs for details

### ⚠️ Slow Performance
**Solution:**
1. The smart caching helps, but first load may be slow
2. Wait 2-3 seconds for initial load
3. Subsequent loads will be instant (cached)
4. Auto-refresh only happens every 5-30 minutes

## Sharing Your App

### Share URL
Send this link to anyone:
```
https://share.streamlit.io/lucydev256/olympics-2026/main/app.py
```

Or if using custom domain:
```
https://olympics-2026-lucy.streamlit.app
```

### Social Media
- Twitter/X: "Check out the Milano-Cortina 2026 Olympics Live Dashboard! 🏅"
- LinkedIn: Share as a project showcase
- GitHub: Star the repository

## Data Updates

The API updates every 10 minutes with the latest results:
- The app uses smart caching to avoid rate limiting
- Cached data expires based on type:
  - Events: 10 minutes
  - Today's events: 5 minutes
  - Sports/Countries: 24 hours

## Upgrading Your API Plan

If you exceed the BASIC plan limits (10,000 requests/month):

Visit: https://rapidapi.com/jxancestral17/api/milano-cortina-2026-olympics-api/pricing

Plans:
- **BASIC**: $0/month (free, 10K requests)
- **PRO**: $9.99/month (100K requests)
- **ULTRA**: $49/month (500K requests)
- **MEGA**: $299/month (unlimited)

No code changes needed - just upgrade and your app continues working!

## Monitoring & Analytics

### Streamlit Cloud Dashboard
- View app metrics: https://share.streamlit.io/
- See deployment history
- Monitor uptime

### RapidAPI Dashboard
- Track API request usage
- View rate limit status
- Monitor response times

## Troubleshooting Deployment

### Check Logs
1. Go to app settings
2. Click "Manage app"
3. View deployment logs at bottom
4. Look for error messages

### Common Log Errors
```
ModuleNotFoundError: No module named 'streamlit'
→ Add to requirements.txt

ImportError: cannot import name 'OlympicsVisualizations' from 'src.visualizations'
→ Check file structure in GitHub
```

### Reset App
If you need a fresh start:
1. Delete the app (Manage app → Delete)
2. Push updated code to GitHub
3. Deploy new app

## Success Checklist

- ✅ Repository pushed to GitHub
- ✅ All files present in main branch
- ✅ requirements.txt has all dependencies
- ✅ App deployed to Streamlit Cloud
- ✅ RAPIDAPI_KEY secret configured
- ✅ API status shows ✅ Connected
- ✅ Events loading in dashboard
- ✅ App accessible via public URL
- ✅ Can share link with others

## Next Steps After Deployment

1. **Customize Theme** - Edit `.streamlit/config.toml`
2. **Add Features** - Extend `src/visualizations.py`
3. **Improve UX** - Modify `app.py` layout
4. **Monitor Usage** - Check Streamlit Cloud dashboard
5. **Gather Feedback** - Add feedback form in app

## Support

**Questions about Streamlit Cloud?**
- Documentation: https://docs.streamlit.io/
- Community: https://discuss.streamlit.io/

**Questions about RapidAPI?**
- API Docs: https://rapidapi.com/jxancestral17/api/milano-cortina-2026-olympics-api
- Support: Contact via RapidAPI dashboard

**GitHub Issues?**
- Repository: https://github.com/lucydev256/olympics-2026
- Create issue with description

---

**Congratulations! 🎉 Your Olympics Dashboard is now live on Streamlit Cloud!**

Remember to share it with friends and enjoy the Milano-Cortina 2026 Winter Olympics!
