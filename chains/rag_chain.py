import os
from langchain_google_genai import ChatGoogleGenerativeAI
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

# Try local HuggingFace embeddings first, then fall back to remote/HuggingFaceHub-backed embeddings
def _get_embeddings_backend():
    try:
        # Preferred: local sentence-transformers backend (fast but requires `sentence-transformers` + `torch`)
        from langchain_community.embeddings import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    except Exception:
        try:
            # Secondary: use LangChain's HuggingFaceHub-backed embeddings (requires `huggingface_hub` and an API token)
            from langchain.embeddings import HuggingFaceHubEmbeddings
            hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
            return HuggingFaceHubEmbeddings(repo_id="sentence-transformers/all-MiniLM-L6-v2", huggingfacehub_api_token=hf_token)
        except Exception:
            # Final fallback: lightweight wrapper using `huggingface_hub.InferenceClient` (no heavy torch install)
            try:
                from huggingface_hub import InferenceClient
                hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
                client = InferenceClient(token=hf_token) if hf_token else InferenceClient()

                class HFRemoteEmbeddings:
                    def __init__(self, model: str = "sentence-transformers/all-MiniLM-L6-v2"):
                        self.model = model
                        self.client = client

                    def embed_documents(self, texts):
                        results = []
                        for t in texts:
                            res = self.client.feature_extraction(self.model, t)
                            # `feature_extraction` may return token-level vectors; if so, average them
                            if isinstance(res, list) and len(res) and isinstance(res[0], list):
                                dim = len(res[0])
                                agg = [0.0] * dim
                                for token_vec in res:
                                    for i, v in enumerate(token_vec):
                                        agg[i] += v
                                agg = [v / len(res) for v in agg]
                                results.append(agg)
                            else:
                                results.append(res)
                        return results

                    def embed_query(self, text):
                        return self.embed_documents([text])[0]

                return HFRemoteEmbeddings()
            except Exception as e:
                print(f"No embeddings backend available: {e}")
                return None


embeddings = _get_embeddings_backend()

# Initialize Pinecone retriever from existing index (only if embeddings backend is available)
try:
    if embeddings is None:
        raise RuntimeError("No embeddings backend configured; skipping Pinecone retriever initialization.")
    print(f"Connecting to Pinecone index: {index_name}...")
    import socket
    socket.setdefaulttimeout(15)  # Set 15 second timeout for socket operations
    docsearch = PineconeVectorStore.from_existing_index(index_name=index_name, embedding=embeddings)
    retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    print(f"✓ Pinecone retriever initialized with index: {index_name}")
except Exception as e:
    print(f"✗ Error initializing Pinecone or embeddings: {e}")
    print("  Please check your PINECONE_API_KEY, HUGGINGFACEHUB_API_TOKEN and network connection")
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
