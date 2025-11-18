# HealthGuru AI Chatbot Setup Instructions

## Overview
HealthGuru is a multimodal conversational AI chatbot for health assistance with integrated agentic RAG (Retrieval-Augmented Generation).

## Prerequisites
- Python 3.8 or higher
- Required API keys (see below)

## Quick Setup

### 1. Install Dependencies
```bash
python setup.py
```

### 2. Configure Environment
Update the `.env` file with your actual API keys:

```env
PINECONE_API_KEY=your_actual_pinecone_key
GOOGLE_API_KEY=your_actual_google_key
GROQ_API_KEY=your_actual_groq_key
TAVILY_API_KEY=your_actual_tavily_key
```

### 3. Set Up Vector Database
```bash
python Pinecone_load.py
```

### 4. Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Required API Keys

### 1. Pinecone API Key
- Visit [Pinecone Console](https://www.pinecone.io/)
- Create a new project
- Get your API key from the dashboard

### 2. Google API Key
- Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
- Create a new API key
- Enable the Gemini API

### 3. Groq API Key
- Visit [Groq Console](https://console.groq.com/)
- Sign up and get your API key

### 4. Tavily API Key (Optional)
- Visit [Tavily](https://tavily.com/)
- Sign up and get your API key
- This is used for web search fallback

## Project Structure

```
├── Agents/                 # AI agents for different tasks
│   ├── query_processing.py
│   ├── response_generation.py
│   ├── retrieval.py
│   ├── routing.py
│   └── state.py
├── chains/                 # LangChain components
│   ├── prompt_templates.py
│   └── rag_chain.py
├── config/                 # Configuration files
│   └── env.py
├── Data/                   # PDF documents for knowledge base
├── static/                 # Static web assets
├── templates/              # HTML templates
├── utils/                  # Utility functions
│   └── image_desc.py
├── workflow/               # Workflow orchestration
│   └── graph.py
├── app.py                  # Main Flask application
├── Pinecone_load.py        # Vector database setup
└── requirements.txt        # Python dependencies
```

## Features

- **Multimodal Input**: Text and image support
- **Health-focused**: Specialized for health-related queries
- **RAG Integration**: Retrieval-Augmented Generation for accurate responses
- **Agentic Architecture**: Multiple AI agents working together
- **Web Search Fallback**: Tavily integration for additional information
- **Voice Input**: Speech recognition support
- **Modern UI**: Clean, responsive web interface

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **API Key Errors**: Verify all API keys are correctly set in `.env`

3. **Pinecone Connection Issues**: Check your Pinecone API key and index name

4. **Model Loading Issues**: Ensure you have sufficient memory for the embedding model

### Logs
Check the `logs/` directory for error logs if the application fails to start.

## Development

### Adding New Features
1. Create new agents in the `Agents/` directory
2. Update the workflow in `workflow/graph.py`
3. Add new routes in `app.py`

### Testing
```bash
# Test the health endpoint
curl http://localhost:5000/health

# Test chat endpoint
curl -X POST http://localhost:5000/chat \
  -F "message=What are the symptoms of diabetes?"
```

## Support
For issues and questions, please check the logs and ensure all API keys are properly configured.
