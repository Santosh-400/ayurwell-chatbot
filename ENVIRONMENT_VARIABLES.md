# Environment Variables Configuration Guide

This document lists all required environment variables for deploying AyurWell application.

## Required Environment Variables

### 1. Google API Key (Required)
**Variable Name:** `GOOGLE_API_KEY`

**Description:** API key for Google Gemini 2.0 Flash model used for LLM responses

**How to get:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Get API Key"
3. Create a new API key or use existing one
4. Copy the key

**Example:**
```
GOOGLE_API_KEY=AIzaSyAbCdEfGhIjKlMnOpQrStUvWxYz1234567
```

---

### 2. Pinecone API Key (Required)
**Variable Name:** `PINECONE_API_KEY`

**Description:** API key for Pinecone vector database to store and retrieve health information embeddings

**How to get:**
1. Sign up at [Pinecone](https://www.pinecone.io/)
2. Go to API Keys section in dashboard
3. Copy your API key

**Example:**
```
PINECONE_API_KEY=12345678-abcd-1234-efgh-123456789abc
```

---

### 3. Pinecone Index Name (Required)
**Variable Name:** `PINECONE_INDEX_NAME`

**Description:** Name of the Pinecone index containing health data

**Default Value:** `ayurwell-health-index`

**How to set:**
1. Use the default name if you've already created the index
2. Or create a new index with dimensions matching your embedding model

**Example:**
```
PINECONE_INDEX_NAME=ayurwell-health-index
```

---

### 4. Tavily API Key (Required)
**Variable Name:** `TAVILY_API_KEY`

**Description:** API key for Tavily web search API used for real-time health information retrieval

**How to get:**
1. Sign up at [Tavily](https://tavily.com/)
2. Get your API key from dashboard
3. Free tier includes 1000 searches/month

**Example:**
```
TAVILY_API_KEY=tvly-AbCdEfGhIjKlMnOpQrStUvWxYz1234567890
```

---

### 5. Flask Environment (Optional)
**Variable Name:** `FLASK_ENV`

**Description:** Flask application environment setting

**Default Value:** `production`

**Options:**
- `production` - For deployed application (recommended)
- `development` - For local development only

**Example:**
```
FLASK_ENV=production
```

---

### 6. Python Version (Optional - Auto-detected)
**Variable Name:** `PYTHON_VERSION`

**Description:** Python version to use in deployment

**Default Value:** `3.11.0`

**Example:**
```
PYTHON_VERSION=3.11.0
```

---

## Setting Environment Variables

### For Render.com:
1. Go to your service dashboard
2. Navigate to "Environment" tab
3. Click "Add Environment Variable"
4. Enter key-value pairs
5. Click "Save Changes"

### For Railway.app:
1. Go to your project
2. Click on "Variables" tab
3. Add each variable
4. Deploy

### For Fly.io:
```bash
fly secrets set GOOGLE_API_KEY=your_key_here
fly secrets set PINECONE_API_KEY=your_key_here
fly secrets set TAVILY_API_KEY=your_key_here
fly secrets set PINECONE_INDEX_NAME=ayurwell-health-index
```

### For Local Development (.env file):
Create a `.env` file in the root directory:

```env
# Google Gemini API
GOOGLE_API_KEY=AIzaSyAbCdEfGhIjKlMnOpQrStUvWxYz1234567

# Pinecone Vector Database
PINECONE_API_KEY=12345678-abcd-1234-efgh-123456789abc
PINECONE_INDEX_NAME=ayurwell-health-index

# Tavily Web Search
TAVILY_API_KEY=tvly-AbCdEfGhIjKlMnOpQrStUvWxYz1234567890

# Flask Configuration
FLASK_ENV=development
```

---

## Environment Variable Validation

To test if your environment variables are set correctly, run:

```python
import os
from dotenv import load_dotenv

load_dotenv()

required_vars = [
    'GOOGLE_API_KEY',
    'PINECONE_API_KEY',
    'PINECONE_INDEX_NAME',
    'TAVILY_API_KEY'
]

for var in required_vars:
    value = os.getenv(var)
    if value:
        print(f"✓ {var} is set")
    else:
        print(f"✗ {var} is NOT set")
```

---

## Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use different API keys** for development and production
3. **Rotate API keys regularly**
4. **Set appropriate rate limits** on your API keys
5. **Monitor API usage** to detect unusual activity
6. **Use secret management** tools for team environments

---

## Troubleshooting

### Issue: "API Key not found" error
**Solution:** Ensure the environment variable is spelled correctly and has no extra spaces

### Issue: Pinecone connection fails
**Solution:** Verify that your Pinecone index exists and the API key has proper permissions

### Issue: Google API quota exceeded
**Solution:** Check your quota limits at Google AI Studio and consider upgrading or rate limiting requests

### Issue: Environment variables not loading
**Solution:** Ensure `.env` file is in the root directory and `python-dotenv` is installed

---

## Cost Considerations (Free Tiers)

- **Google Gemini API:** 60 requests per minute (free tier)
- **Pinecone:** 1 index, 100K vectors (free tier)
- **Tavily API:** 1000 searches/month (free tier)
- **Render.com:** 750 hours/month (free tier)

Monitor your usage to stay within free tier limits!
