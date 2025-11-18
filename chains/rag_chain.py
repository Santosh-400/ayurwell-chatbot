import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from .prompt_templates import rag_prompt
try:
    from langchain_tavily import TavilySearchResults
except ImportError:
    from langchain_community.tools.tavily_search import TavilySearchResults

# Get env variables safely (fall back to sensible defaults)
index_name = os.getenv("index_name", "ayurwell")
# Prefer explicit default but do not allow legacy model names to be used from environment.
env_model = os.getenv("model")
if env_model and "gemini-1.5" in env_model:
    print(f"Warning: environment 'model' is set to legacy value '{env_model}' — overriding to gemini-2.0-flash-001")
# Use a model that is available for this account / API version
# (confirmed via REST model list): gemini-2.0-flash-001
model = "gemini-2.0-flash-001"

# Use Google's embeddings instead of HuggingFace (lighter and cloud-friendly)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Initialize Pinecone retriever from existing index
try:
    docsearch = PineconeVectorStore.from_existing_index(index_name=index_name, embedding=embeddings)
    retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    print(f"Pinecone retriever initialized with index: {index_name}")
except Exception as e:
    print(f"Error initializing Pinecone: {e}")
    print("Please check your PINECONE_API_KEY and ensure the index exists")
    retriever = None

# Initialize Tavily search (with fallback if API key is missing)
try:
    tavily_search = TavilySearchResults(max_results=3)
except Exception as e:
    print(f"Warning: Tavily search not available: {e}")
    tavily_search = None

try:
    llm = ChatGoogleGenerativeAI(model=model, temperature=0.3, max_tokens=1024)
    print(f"LLM initialized with model: {model}")
except Exception as e:
    print(f"Error initializing LLM: {e}")
    print("Please check your GOOGLE_API_KEY in .env file")
    llm = None

rag_chain = rag_prompt | llm

__all__ = ["llm", "retriever", "rag_chain", "tavily_search"]
