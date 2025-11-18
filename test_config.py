#!/usr/bin/env python3
"""
Test configuration and API keys
"""

import os
from dotenv import load_dotenv

def test_configuration():
    """Test if all required configurations are set"""
    print("Testing AyurWell Configuration...")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check API keys
    api_keys = {
        'PINECONE_API_KEY': os.getenv('PINECONE_API_KEY'),
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
        'GROQ_API_KEY': os.getenv('GROQ_API_KEY'),
        'TAVILY_API_KEY': os.getenv('TAVILY_API_KEY')
    }
    
    print("API Keys Status:")
    for key, value in api_keys.items():
        if value and value != f"your_{key.lower()}_here":
            print(f"[OK] {key}: Set")
        else:
            print(f"[MISSING] {key}: Not set or using default value")
    
    print("\nModel Configuration:")
    model = os.getenv('model', 'emini-2.0-flash-live-001')
    print(f"[OK] Model: {model}")
    
    index_name = os.getenv('index_name', 'AyurWell')
    print(f"[OK] Pinecone Index: {index_name}")
    
    print("\nTesting Imports...")
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("[OK] Google Generative AI: Available")
    except ImportError as e:
        print(f"[ERROR] Google Generative AI: {e}")
    
    try:
        from langchain_pinecone import PineconeVectorStore
        print("[OK] Pinecone: Available")
    except ImportError as e:
        print(f"[ERROR] Pinecone: {e}")
    
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        print("[OK] HuggingFace Embeddings: Available")
    except ImportError as e:
        print(f"[ERROR] HuggingFace Embeddings: {e}")
    
    print("\n" + "=" * 40)
    print("Configuration test completed!")
    
    # Check if all required keys are set
    missing_keys = [key for key, value in api_keys.items() 
                   if not value or value == f"your_{key.lower()}_here"]
    
    if missing_keys:
        print(f"\n[WARNING] Missing API keys: {', '.join(missing_keys)}")
        print("Please update your .env file with actual API keys")
        return False
    else:
        print("\n[SUCCESS] All configurations look good!")
        return True

if __name__ == "__main__":
    test_configuration()
