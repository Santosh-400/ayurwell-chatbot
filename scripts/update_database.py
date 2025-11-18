import os
import argparse
from dotenv import load_dotenv

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Add new documents to Pinecone index")
    parser.add_argument("--new-docs", required=True, help="Directory containing new documents to index")
    parser.add_argument("--index-name", default=os.getenv("index_name", os.getenv("PINECONE_INDEX_NAME", "AyurWell")), help="Pinecone index name")
    args = parser.parse_args()

    try:
        from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain_pinecone import PineconeVectorStore
        from langchain.embeddings import HuggingFaceEmbeddings
    except Exception as e:
        print(f"Missing libraries: {e}")
        raise

    loader = DirectoryLoader(args.new_docs, glob="**/*.pdf", loader_cls=PyPDFLoader)
    docs = loader.load()
    print(f"Loaded {len(docs)} new documents")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(docs)
    print(f"Split into {len(chunks)} chunks")

    embeddings = HuggingFaceEmbeddings(model_name=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"))
    vectordb = PineconeVectorStore.from_documents(documents=chunks, index_name=args.index_name, embedding=embeddings)
    print(f"Upserted {len(chunks)} chunks to Pinecone index '{args.index_name}'")


if __name__ == "__main__":
    main()
