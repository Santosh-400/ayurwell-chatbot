# 🚀 AyurWell Deployment Guide

Complete guide to deploy your AyurWell application on free cloud platforms.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Option 1: Deploy on Render (Recommended)](#option-1-deploy-on-render-recommended)
4. [Option 2: Deploy on Railway](#option-2-deploy-on-railway)
5. [Option 3: Deploy on Fly.io](#option-3-deploy-on-flyio)
6. [Option 4: Deploy on PythonAnywhere](#option-4-deploy-on-pythonanywhere)
7. [Post-Deployment Steps](#post-deployment-steps)
8. [Troubleshooting](#troubleshooting)
9. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Prerequisites

Before deploying, ensure you have:

- ✅ GitHub account (to host your code)
- ✅ Google API Key ([Get it here](https://makersuite.google.com/app/apikey))
- ✅ Pinecone API Key ([Sign up](https://www.pinecone.io/))
- ✅ Tavily API Key ([Sign up](https://tavily.com/))
- ✅ Your Pinecone index created and populated with health data

---

## Pre-Deployment Checklist

### 1. Push Code to GitHub

```powershell
# Initialize git if not already done
git init

# Add all files
git add .

# Commit changes
git commit -m "Prepare for deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### 2. Verify Required Files

Ensure these files exist in your repository:
- ✅ `render.yaml` - Render configuration
- ✅ `Dockerfile` - Docker configuration
- ✅ `requirements-prod.txt` - Production dependencies
- ✅ `Procfile` - Process configuration
- ✅ `.dockerignore` - Docker ignore rules
- ✅ `app.py` - Main application file

### 3. Test Locally (Optional)

```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install production requirements
pip install -r requirements-prod.txt

# Set environment variables (create .env file)
# See ENVIRONMENT_VARIABLES.md for details

# Test the app
python app.py
```

---

## Option 1: Deploy on Render (Recommended)

**Pros:** Easy setup, automatic deployments, good free tier  
**Cons:** Cold starts after 15 min inactivity  
**Free Tier:** 750 hours/month

### Step-by-Step Instructions:

#### 1. Sign Up for Render
1. Go to [render.com](https://render.com/)
2. Sign up using your GitHub account
3. Authorize Render to access your repositories

#### 2. Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Select the AyurWell repository

#### 3. Configure the Service

**Basic Settings:**
- **Name:** `ayurwell-app` (or any name you prefer)
- **Region:** Choose closest to your users
- **Branch:** `main`
- **Runtime:** `Python 3`

**Build Settings:**
- **Build Command:** `pip install -r requirements-prod.txt`
- **Start Command:** `gunicorn app:app`

Alternatively, Render will auto-detect `render.yaml` and use those settings.

#### 4. Set Environment Variables

Go to **"Environment"** tab and add:

```
GOOGLE_API_KEY=your_google_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=ayurwell-health-index
TAVILY_API_KEY=your_tavily_api_key_here
FLASK_ENV=production
```

#### 5. Deploy
1. Click **"Create Web Service"**
2. Wait 5-10 minutes for initial deployment
3. Your app will be available at: `https://ayurwell-app.onrender.com`

#### 6. Enable Auto-Deploy (Optional)
1. Go to **"Settings"** → **"Build & Deploy"**
2. Enable **"Auto-Deploy"** for automatic updates on git push

---

## Option 2: Deploy on Railway

**Pros:** Simple deployment, $5/month free credit  
**Cons:** Limited free credits  
**Free Tier:** $5 credit/month

### Step-by-Step Instructions:

#### 1. Sign Up for Railway
1. Go to [railway.app](https://railway.app/)
2. Sign up with GitHub

#### 2. Create New Project
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your AyurWell repository

#### 3. Add Environment Variables
1. Click on your service
2. Go to **"Variables"** tab
3. Add all required variables (see ENVIRONMENT_VARIABLES.md)

#### 4. Configure Deployment
Railway auto-detects Python apps. Ensure:
- Build command: `pip install -r requirements-prod.txt`
- Start command: `gunicorn app:app --bind 0.0.0.0:$PORT`

#### 5. Deploy
1. Railway automatically deploys
2. Access via the provided URL
3. Enable custom domain if needed

---

## Option 3: Deploy on Fly.io

**Pros:** Good performance, supports Docker  
**Cons:** Requires Docker knowledge  
**Free Tier:** 3 shared-cpu VMs, 3GB storage

### Step-by-Step Instructions:

#### 1. Install Fly CLI

```powershell
# Install via PowerShell
iwr https://fly.io/install.ps1 -useb | iex
```

#### 2. Sign Up & Login

```powershell
fly auth signup
# Or if you have an account:
fly auth login
```

#### 3. Launch Your App

```powershell
# Navigate to your project directory
cd "D:\PES\sem-7\AI in HealthCare\Ayur"

# Initialize Fly app (creates fly.toml)
fly launch --name ayurwell-app --region sin
```

Answer the prompts:
- Use existing Dockerfile? **Yes**
- Create .dockerignore? **No** (already exists)
- Would you like to set up a database? **No**

#### 4. Set Environment Variables

```powershell
fly secrets set GOOGLE_API_KEY="your_google_api_key"
fly secrets set PINECONE_API_KEY="your_pinecone_api_key"
fly secrets set PINECONE_INDEX_NAME="ayurwell-health-index"
fly secrets set TAVILY_API_KEY="your_tavily_api_key"
fly secrets set FLASK_ENV="production"
```

#### 5. Deploy

```powershell
fly deploy
```

#### 6. Open Your App

```powershell
fly open
```

Your app will be at: `https://ayurwell-app.fly.dev`

---

## Option 4: Deploy on PythonAnywhere

**Pros:** Python-specific, very simple  
**Cons:** Limited resources, API restrictions  
**Free Tier:** 1 web app, 512MB storage

### Step-by-Step Instructions:

#### 1. Sign Up
1. Go to [pythonanywhere.com](https://www.pythonanywhere.com/)
2. Create a free account

#### 2. Upload Code
1. Go to **"Files"** tab
2. Upload your project or clone from GitHub:
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

#### 3. Create Virtual Environment
Open a Bash console:
```bash
cd YOUR_REPO
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements-prod.txt
```

#### 4. Configure Web App
1. Go to **"Web"** tab
2. Click **"Add a new web app"**
3. Choose **"Manual configuration"**
4. Select **"Python 3.11"**

#### 5. Set Up WSGI File
Edit the WSGI configuration file:
```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/YOUR_REPO'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['GOOGLE_API_KEY'] = 'your_key'
os.environ['PINECONE_API_KEY'] = 'your_key'
os.environ['PINECONE_INDEX_NAME'] = 'ayurwell-health-index'
os.environ['TAVILY_API_KEY'] = 'your_key'

# Import Flask app
from app import app as application
```

#### 6. Reload & Access
1. Click **"Reload"** button
2. Access at: `https://YOUR_USERNAME.pythonanywhere.com`

**Note:** Free tier has API restrictions. External API calls may be limited.

---

## Post-Deployment Steps

### 1. Test Your Deployment

```powershell
# Test the health endpoint
curl https://your-app-url.com/

# Test the API (if applicable)
curl -X POST https://your-app-url.com/api/chat -H "Content-Type: application/json" -d '{"message":"Hello"}'
```

### 2. Set Up Custom Domain (Optional)

**Render:**
1. Go to **"Settings"** → **"Custom Domains"**
2. Add your domain
3. Update DNS records

**Railway/Fly.io:** Similar process in their dashboards

### 3. Enable HTTPS
Most platforms provide free SSL/TLS certificates automatically.

### 4. Set Up Monitoring

**Render:**
- Built-in metrics available in dashboard
- Set up email alerts for downtime

**Fly.io:**
```powershell
fly dashboard -a ayurwell-app
```

### 5. Configure Logging

Logs are available in each platform's dashboard:
- **Render:** "Logs" tab
- **Railway:** "Deployments" → "Logs"
- **Fly.io:** `fly logs`

---

## Troubleshooting

### Common Issues & Solutions

#### 1. Build Fails - Missing Dependencies

**Error:** `ModuleNotFoundError: No module named 'xyz'`

**Solution:**
- Add missing package to `requirements-prod.txt`
- Push changes to GitHub
- Redeploy

#### 2. Application Crashes on Startup

**Error:** `Application failed to start`

**Solution:**
- Check logs for specific error
- Verify all environment variables are set
- Ensure Pinecone index exists and is accessible

#### 3. Memory Limit Exceeded

**Error:** `Out of memory` or `Process killed`

**Solution:**
- Remove heavy dependencies from requirements
- Use API-based embeddings instead of local models
- Upgrade to paid tier if necessary

#### 4. Cold Start Issues (Render)

**Problem:** App takes 30+ seconds to respond after inactivity

**Solution:**
- Accept as limitation of free tier
- Use UptimeRobot to ping app every 14 minutes (keeps it warm)
- Or upgrade to paid tier for always-on instance

#### 5. API Rate Limits

**Error:** `429 Too Many Requests`

**Solution:**
- Implement rate limiting in your app
- Cache responses when possible
- Monitor API usage
- Upgrade API tiers if needed

#### 6. Database Connection Fails

**Error:** `Failed to connect to Pinecone`

**Solution:**
- Verify `PINECONE_API_KEY` is correct
- Check `PINECONE_INDEX_NAME` matches your index
- Ensure index is in correct environment (free tier uses specific regions)
- Test connection with a simple script

#### 7. Port Binding Issues

**Error:** `Address already in use`

**Solution:**
Ensure your `app.py` uses environment PORT:
```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

---

## Monitoring & Maintenance

### 1. Set Up Uptime Monitoring

Use [UptimeRobot](https://uptimerobot.com/) (free):
1. Sign up for free account
2. Add HTTP(s) monitor for your URL
3. Set check interval to 5 minutes
4. Get alerts via email/SMS

### 2. Monitor API Usage

**Google Gemini:**
- Check quota at [Google AI Studio](https://makersuite.google.com/)

**Pinecone:**
- Monitor at [Pinecone Console](https://app.pinecone.io/)

**Tavily:**
- Check usage at [Tavily Dashboard](https://app.tavily.com/)

### 3. Review Logs Regularly

Set up daily/weekly log review:
```powershell
# For Fly.io
fly logs --app ayurwell-app

# For Render - check dashboard
```

### 4. Update Dependencies

Monthly maintenance:
```powershell
# Update requirements
pip list --outdated
pip install --upgrade package-name

# Test locally
python app.py

# Update requirements-prod.txt
pip freeze > requirements-prod.txt

# Deploy updates
git add requirements-prod.txt
git commit -m "Update dependencies"
git push
```

### 5. Backup Your Data

- Export Pinecone index periodically
- Keep backup of environment variables
- Version control all code changes

---

## Performance Optimization Tips

### 1. Enable Caching
Add caching to reduce API calls:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_response(query):
    # Your logic here
    pass
```

### 2. Implement Request Queuing
Limit concurrent requests to avoid memory issues.

### 3. Use CDN for Static Assets
Host images, CSS, JS on CDN (Cloudflare, etc.)

### 4. Optimize Database Queries
- Use appropriate Pinecone namespace
- Limit top_k results
- Filter metadata efficiently

### 5. Compress Responses
Enable gzip compression in Flask:
```python
from flask_compress import Compress
Compress(app)
```

---

## Cost Estimation (Free Tiers)

| Service | Free Tier Limit | Est. Users Supported |
|---------|----------------|---------------------|
| Render | 750 hrs/month | 100-500/day |
| Railway | $5 credit/month | 50-200/day |
| Fly.io | 3 VMs, 160GB | 200-1000/day |
| Google Gemini | 60 req/min | ~2000 queries/day |
| Pinecone | 100K vectors | Unlimited reads |
| Tavily | 1000 searches/month | 30/day |

**Tips to stay within limits:**
- Implement rate limiting
- Cache responses
- Use client-side processing where possible
- Monitor usage daily

---

## Scaling Beyond Free Tier

When you outgrow free tier:

### Option 1: Upgrade Current Platform
- Render: $7/month for Starter
- Railway: $5/month + usage
- Fly.io: Pay-as-you-go

### Option 2: Move to AWS/GCP/Azure
- More control and scalability
- Higher complexity
- Costs start at $10-20/month

### Option 3: Optimize Current Setup
- Implement aggressive caching
- Reduce API calls
- Use serverless functions for specific tasks

---

## Security Checklist

Before going live:

- ✅ All API keys in environment variables (not hardcoded)
- ✅ HTTPS enabled (automatic on most platforms)
- ✅ CORS properly configured
- ✅ Input validation implemented
- ✅ Rate limiting enabled
- ✅ Error messages don't expose sensitive info
- ✅ Dependencies updated to latest secure versions
- ✅ `.env` file in `.gitignore`

---

## Support & Resources

### Official Documentation
- [Render Docs](https://render.com/docs)
- [Railway Docs](https://docs.railway.app/)
- [Fly.io Docs](https://fly.io/docs/)
- [PythonAnywhere Help](https://help.pythonanywhere.com/)

### Community Support
- [Render Community](https://community.render.com/)
- [Railway Discord](https://discord.gg/railway)
- [Fly.io Community](https://community.fly.io/)

### Debugging Tools
- [Render Status](https://status.render.com/)
- [Railway Status](https://status.railway.app/)
- Browser DevTools for frontend issues
- Platform logs for backend issues

---

## Quick Reference Commands

### Git Operations
```powershell
git add .
git commit -m "Update deployment config"
git push origin main
```

### Fly.io Commands
```powershell
fly logs                    # View logs
fly status                  # Check status
fly scale count 2           # Scale instances
fly secrets list            # List secrets
fly deploy                  # Deploy updates
```

### Testing Endpoints
```powershell
# Test homepage
curl https://your-app.com/

# Test with data
curl -X POST https://your-app.com/api/endpoint -H "Content-Type: application/json" -d '{}'
```

---

## Conclusion

You now have everything needed to deploy AyurWell on free cloud platforms! 

**Recommended Path:**
1. Start with **Render** (easiest, most reliable)
2. Test with small traffic
3. Monitor usage and performance
4. Scale up or optimize as needed

**Need help?** Check the troubleshooting section or review platform documentation.

**Good luck with your deployment! 🚀**

---

*Last Updated: November 2025*
