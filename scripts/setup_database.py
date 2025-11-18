import os
import argparse
from dotenv import load_dotenv

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Create and populate Pinecone index from documents")
    parser.add_argument("--source-dir", required=True, help="Directory containing documents (pdf, txt)")
    parser.add_argument("--index-name", default=os.getenv("index_name", os.getenv("PINECONE_INDEX_NAME", "ayurwell")), help="Pinecone index name")
    args = parser.parse_args()

    # Lazy import heavy libraries
    try:
        from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain_pinecone import PineconeVectorStore
        from langchain.embeddings import HuggingFaceEmbeddings
    except Exception as e:
        print(f"Missing libraries: {e}")
        raise

    source_dir = args.source_dir
    index_name = args.index_name

    print(f"Loading documents from {source_dir}")
    loader = DirectoryLoader(source_dir, glob="**/*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    print(f"Loaded {len(documents)} documents")

    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)
    print(f"Created {len(docs)} chunks")

    print("Initializing embeddings and Pinecone vector store...")
    embeddings = HuggingFaceEmbeddings(model_name=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"))

    # Ensure Pinecone index exists (create if missing)
    try:
        import pinecone

        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        pinecone_env = os.getenv("PINECONE_ENVIRONMENT") or os.getenv("PINECONE_REGION")
        if not pinecone_api_key:
            print("Warning: PINECONE_API_KEY not set in environment; continuing and hoping client is already configured.")

        existing_indexes = []

        # Handle older pinecone client (has init/list_indexes) and newer pinecone client (Pinecone class)
        try:
            if hasattr(pinecone, "init"):
                # older client
                try:
                    pinecone.init(api_key=pinecone_api_key, environment=pinecone_env)
                except Exception:
                    # ignore and proceed; list_indexes may still work if env is configured
                    pass
                try:
                    existing_indexes = pinecone.list_indexes()
                except Exception:
                    existing_indexes = []
            elif hasattr(pinecone, "Pinecone"):
                # newer client
                try:
                    pc = pinecone.Pinecone(api_key=pinecone_api_key)
                except Exception:
                    pc = None
                if pc is not None:
                    try:
                        idx_resp = pc.list_indexes()
                        if isinstance(idx_resp, list):
                            existing_indexes = idx_resp
                        elif hasattr(idx_resp, "names"):
                            existing_indexes = idx_resp.names()
                        elif hasattr(idx_resp, "indexes"):
                            existing_indexes = idx_resp.indexes
                        else:
                            existing_indexes = []
                    except Exception:
                        existing_indexes = []
            else:
                existing_indexes = []
        except Exception:
            existing_indexes = []

        if index_name not in existing_indexes:
            print(f"Pinecone index '{index_name}' not found. Attempting to create index...")
            # try to infer embedding dimension from the embeddings object
            try:
                test_vec = embeddings.embed_query("test")
                dim = len(test_vec)
            except Exception:
                dim = int(os.getenv("EMBEDDING_DIM", 384))

            metric = os.getenv("PINECONE_METRIC", "cosine")

            created = False
            # Try old create_index call first
            try:
                if hasattr(pinecone, "create_index"):
                    pinecone.create_index(name=index_name, dimension=dim, metric=metric)
                    created = True
                else:
                    # Try newer Pinecone client API
                    try:
                        from pinecone import Pinecone, ServerlessSpec
                        try:
                            pc = Pinecone(api_key=pinecone_api_key)
                        except TypeError:
                            # older constructor signature fallback
                            pc = Pinecone(pinecone_api_key)

                        # Try simple create_index
                        try:
                            pc.create_index(name=index_name, dimension=dim, metric=metric)
                            created = True
                        except TypeError:
                            # Try with ServerlessSpec; infer region if possible
                            region = pinecone_env or os.getenv("PINECONE_REGION", "us-west1")
                            try:
                                pc.create_index(name=index_name, dimension=dim, metric=metric, spec=ServerlessSpec(cloud="aws", region=region))
                                created = True
                            except Exception as e:
                                print(f"Failed to create index via new client with ServerlessSpec: {e}")
                    except Exception as e:
                        print(f"New-style Pinecone client not available or failed: {e}")
            except Exception as e:
                print(f"Failed to create Pinecone index (unexpected error): {e}")
            except Exception as e:
                print(f"Failed to create Pinecone index '{index_name}': {e}")

            if created:
                print(f"Created Pinecone index '{index_name}' with dimension={dim}")
            else:
                print(f"Could not automatically create Pinecone index '{index_name}'. Please create it manually in your Pinecone console and re-run this script.")

    except Exception as e:
        print(f"Pinecone client not available or initialization failed: {e}")

    # Create or use existing index and upload
    vectordb = PineconeVectorStore.from_documents(documents=docs, index_name=index_name, embedding=embeddings)
    print(f"Uploaded {len(docs)} chunks to Pinecone index '{index_name}'")


if __name__ == "__main__":
    main()
