# 🧠 AyurWell - Multimodal Conversational AI Chatbot for Health Assistance


## 🏥 Overview

AyurWell is an advanced multimodal conversational AI chatbot designed to provide comprehensive health assistance through an integrated Agentic RAG (Retrieval-Augmented Generation) system. The system combines multiple AI techniques including Natural Language Processing, vector embeddings, and multi-agent orchestration to deliver accurate, contextual health information.

## ✨ Key Features

- **Multimodal Input Support**: Text, voice commands, and image uploads
- **Comprehensive Health Database**: Curated from trusted sources (Mayo Clinic, NIH, MedlinePlus, PubMed)
- **Multi-Agent Architecture**: Intelligent routing with specialized agents
- **Real-time Web Search**: Fallback mechanism for latest health information
- **Voice Recognition**: Speech-to-text capabilities
- **Image Analysis**: Medical image context extraction using LLaMA-4 Scout
- **Retrieval-Augmented Generation**: Reduces hallucination with factual grounding

## 🏗️ System Architecture

The system employs a modular, agent-driven architecture with the following components:

### Core Agents
- **Query Refinement Agent**: Cleans and reformulates ambiguous inputs
- **Query Categorization Agent**: Classifies health vs non-health queries
- **Retrieval Agent**: Searches Pinecone vector database
- **Web Search Agent**: Real-time information retrieval via Tavily API
- **Off-topic Handler**: Manages non-health related queries
- **Greeting Agent**: Handles casual interactions
- **Generator Agent**: Produces final text responses

### Technology Stack
- **LLM**: Google Gemini 2.0 Flash
- **Vector Database**: Pinecone
- **Agent Framework**: LangGraph & LangChain
- **Image Analysis**: LLaMA-4 Scout
- **Web Search**: Tavily Search API
- **Voice Recognition**: Google Web Speech API
- **UI Framework**: Custom web-based interface

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Internet connection for API access

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/AyurWell.git
   cd healthguru
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   # API Keys
   GEMINI_API_KEY=your_gemini_api_key_here
   PINECONE_API_KEY=your_pinecone_api_key_here
   PINECONE_ENVIRONMENT=your_pinecone_environment
   TAVILY_API_KEY=your_tavily_search_api_key
   LLAMA_API_KEY=your_llama_api_key_here
   
   # Vector Database Configuration
   PINECONE_INDEX_NAME=healthguru-index
   
   # Model Configuration
   EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   ```

4. **Initialize the vector database** (First-time setup)
   ```bash
   python setup_database.py
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your browser and navigate to `http://localhost:7860`

## 📋 Requirements

The `requirements.txt` file should include:

```
# Core Dependencies
langchain>=0.1.0
langgraph>=0.0.20
pinecone-client>=3.0.0
gradio>=4.0.0
google-generativeai>=0.3.0

# NLP and Embeddings
sentence-transformers>=2.2.0
spacy>=3.7.0
nltk>=3.8.0
transformers>=4.30.0

# Data Processing
pandas>=2.0.0
numpy>=1.24.0
pdfplumber>=0.9.0
beautifulsoup4>=4.12.0

# Web and API
requests>=2.31.0
tavily-python>=0.3.0
speech-recognition>=3.10.0

# Image Processing
Pillow>=10.0.0
opencv-python>=4.8.0

# Utilities
python-dotenv>=1.0.0
tqdm>=4.65.0
jsonschema>=4.17.0
```

## 🔧 Configuration

### API Key Setup

1. **Google Gemini API**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Generate your API key
   - Add to `.env` file

2. **Pinecone**
   - Sign up at [Pinecone](https://www.pinecone.io/)
   - Create a new index with 384 dimensions
   - Get your API key and environment

3. **Tavily Search API**
   - Register at [Tavily](https://tavily.com/)
   - Generate API key for web search functionality

4. **LLaMA API** (for image analysis)
   - Obtain access to LLaMA-4 Scout
   - Configure API credentials

### Database Initialization

Run the database setup script to populate the vector database:

```bash
python scripts/setup_database.py --source-dir ./data/health_docs
```

## 🎯 Usage Examples

### Text Queries
```
User: "What are the symptoms of diabetes?"
HealthGuru: [Provides comprehensive diabetes symptoms from trusted sources]
```

### Voice Input
- Click the microphone button
- Speak your health question
- The system will transcribe and process your query

### Image Upload
- Upload medical images or prescription photos
- The system analyzes visual content and provides relevant information

## 🔍 System Workflow

1. **Input Processing**: Accepts text, voice, or image inputs
2. **Query Refinement**: Cleans and reformulates user queries
3. **Classification**: Determines if query is health-related
4. **Information Retrieval**: Searches vector database or web
5. **Response Generation**: Uses RAG to provide accurate answers
6. **Output Delivery**: Returns multimodal responses to user

## 📊 Performance Considerations

- **Latency**: Sequential agent calls may introduce delays
- **Accuracy**: RAG system reduces hallucination significantly
- **Scalability**: Modular architecture supports easy extension

## 🛠️ Development

### Project Structure
```
healthguru/
├── app.py                 # Main application entry point
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (create this)
├── agents/               # Agent implementations
│   ├── query_agent.py
│   ├── retrieval_agent.py
│   └── generation_agent.py
├── data/                 # Health documentation
├── scripts/              # Setup and utility scripts
├── static/               # Web UI assets
└── templates/            # HTML templates
```

### Adding New Health Data Sources

1. Place documents in `./data/health_docs/`
2. Run the database update script:
   ```bash
   python scripts/update_database.py --new-docs ./data/health_docs/new_folder
   ```

## 🚨 Troubleshooting

### Common Issues

1. **API Key Errors**
   - Verify all API keys in `.env` file
   - Check API key permissions and quotas

2. **Database Connection Issues**
   - Ensure Pinecone index is created
   - Verify network connectivity

3. **Voice Recognition Not Working**
   - Check microphone permissions
   - Ensure stable internet connection

4. **Slow Response Times**
   - Consider using lighter models for development
   - Implement caching mechanisms

### Error Logs
Check `logs/healthguru.log` for detailed error information.

## ⚠️ Important Disclaimers

- **Medical Advice**: HealthGuru provides informational content only and should not replace professional medical advice
- **Emergency Situations**: Always contact emergency services for urgent medical needs
- **Data Privacy**: Ensure compliance with healthcare data regulations in your region

## 🔮 Future Enhancements

- Formal evaluation using DeepEval/RAGAS
- User personalization and health history tracking
- Latency optimization through caching
- Advanced reasoning with ToT and CoT agents
- Multilingual support with XLM-R/mBERT


## 🙏 Acknowledgments

- Mayo Clinic, NIH, MedlinePlus, PubMed for health data sources
- Google for Gemini AI models
- Pinecone for vector database services
- The open-source community for various libraries and tools

---

**Built with ❤️ by the HealthGuru Team at PES University**

*Making healthcare information accessible through AI*
