#!/usr/bin/env python3
"""
Script to create .env file for AyurWell
"""

import os

def create_env_file():
    """Create .env file with proper configuration"""
    env_content = """# API Keys - Replace with your actual API keys
PINECONE_API_KEY=your_pinecone_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# Pinecone Configuration
PINECONE_INDEX_NAME=AyurWell
index_name=AyurWell

# Model Configuration
model=gemini-2.0-flash-live-001
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    print("Created .env file")
    print("Please update .env file with your actual API keys before running the application")

if __name__ == "__main__":
    create_env_file()
