#!/usr/bin/env python3
"""
Test script to verify HealthGuru setup
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test if environment variables are loaded"""
    print("🔍 Testing environment setup...")
    
    load_dotenv()
    
    required_vars = [
        'PINECONE_API_KEY',
        'GOOGLE_API_KEY', 
        'GROQ_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var) == f"your_{var.lower()}_here":
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing or not configured: {', '.join(missing_vars)}")
        print("Please update your .env file with actual API keys")
        return False
    else:
        print("✅ Environment variables configured")
        return True

def test_imports():
    """Test if required packages can be imported"""
    print("🔍 Testing package imports...")
    
    packages = [
        'flask',
        'flask_cors',
        'langchain',
        'langchain_core',
        'langchain_community',
        'langchain_google_genai',
        'langchain_pinecone',
        'pinecone',
        'PIL',
        'requests'
    ]
    
    failed_imports = []
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            failed_imports.append(package)
    
    if failed_imports:
        print(f"❌ Failed to import: {', '.join(failed_imports)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All packages imported successfully")
        return True

def test_directories():
    """Test if required directories exist"""
    print("🔍 Testing directory structure...")
    
    required_dirs = [
        'uploads',
        'logs', 
        'static',
        'templates',
        'Agents',
        'chains',
        'workflow',
        'utils'
    ]
    
    missing_dirs = []
    for directory in required_dirs:
        if not os.path.exists(directory):
            missing_dirs.append(directory)
    
    if missing_dirs:
        print(f"❌ Missing directories: {', '.join(missing_dirs)}")
        return False
    else:
        print("✅ Directory structure is correct")
        return True

def test_files():
    """Test if required files exist"""
    print("🔍 Testing required files...")
    
    required_files = [
        'app.py',
        'requirements.txt',
        'Agents/state.py',
        'Agents/query_processing.py',
        'Agents/retrieval.py',
        'Agents/response_generation.py',
        'Agents/routing.py',
        'chains/rag_chain.py',
        'chains/prompt_templates.py',
        'workflow/graph.py',
        'utils/image_desc.py',
        'templates/ui.html'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files present")
        return True

def main():
    print("🧪 HealthGuru Setup Test")
    print("=" * 40)
    
    tests = [
        test_environment,
        test_imports, 
        test_directories,
        test_files
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! HealthGuru is ready to run.")
        print("\nNext steps:")
        print("1. Run: python Pinecone_load.py")
        print("2. Run: python app.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
