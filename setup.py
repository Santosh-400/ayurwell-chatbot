#!/usr/bin/env python3
"""
Setup script for AyurWell AI Chatbot
This script helps set up the environment and install dependencies
"""

import os
import subprocess
import sys

def create_env_file():
    """Create .env file with template values"""
    env_content = """# API Keys - Replace with your actual API keys
PINECONE_API_KEY=your_pinecone_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# Pinecone Configuration
PINECONE_INDEX_NAME=healthguru
index_name=healthguru

# Model Configuration
model=gemini-2.0-flash-live-001
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file with template values")
        print("⚠️  Please update .env file with your actual API keys")
    else:
        print("✅ .env file already exists")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    return True

def setup_directories():
    """Create necessary directories"""
    directories = ['uploads', 'logs', 'static', 'templates']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    print("✅ Created necessary directories")

def main():
    print("🚀 Setting up AyurWell AI Chatbot...")
    print("=" * 50)
    
    # Create .env file
    create_env_file()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed. Please check the error messages above.")
        return
    
    # Setup directories
    setup_directories()
    
    print("=" * 50)
    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update .env file with your actual API keys")
    print("2. Run: python Pinecone_load.py (to set up the vector database)")
    print("3. Run: python app.py (to start the application)")
    print("\n🔑 Required API keys:")
    print("- PINECONE_API_KEY: Get from https://www.pinecone.io/")
    print("- GOOGLE_API_KEY: Get from https://makersuite.google.com/app/apikey")
    print("- GROQ_API_KEY: Get from https://console.groq.com/")
    print("- TAVILY_API_KEY: Get from https://tavily.com/")

if __name__ == "__main__":
    main()
