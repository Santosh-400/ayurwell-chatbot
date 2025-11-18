from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeVectorStore

import os
from dotenv import load_dotenv
load_dotenv()


PINECONE_API_KEY=os.environ.get('PINECONE_API_KEY')
# GOOGLE_API_KEY=os.environ.get('GOOGLE_API_KEY')

#extract Data from the pdf file
def load_pdf_file(data):
    loader=DirectoryLoader(data,glob="*.pdf",loader_cls=PyPDFLoader)
    documents=loader.load()
    return documents

extracted_data=load_pdf_file(data='Data/')

# print(extracted_data)

#text splitting into chunks
def text_split(extracted_data):
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=20)
    text_chunks=text_splitter.split_documents(extracted_data)
    return text_chunks

text_chunks=text_split(extracted_data)
# print("length of the chunk is ",len(text_chunks))
# print(text_chunks)

#embedding models to convert to embeddings from the huggingface note the dimension of the vector model need in pinnecone
#384 dimension vector
def download_hugging_face_embeddings():
    embeddings=HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    return embeddings

embeddings=download_hugging_face_embeddings()
# print(embeddings)


#to check the embedding working or not

# query_result=embeddings.embed_query("hello world")
# print("length",query_result,len(query_result))

#create an index in pinecone database
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "AyurWell"

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384, # Replace with your model dimensions
        metric="cosine", # Replace with your model metric
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        ) 
    )

docsearch=PineconeVectorStore.from_documents(
    documents=text_chunks,
    index_name=index_name,
    embedding=embeddings,

)

result = docsearch.similarity_search("diabetes treatment", k=3)
for doc in result:
    print(doc.page_content)
