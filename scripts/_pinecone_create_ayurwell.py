from dotenv import load_dotenv
import os
load_dotenv()

print('Creating Pinecone index AyurWell using installed pinecone client...')
try:
    import pinecone
    from pinecone import Pinecone
    try:
        pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
    except TypeError:
        pc = Pinecone(os.getenv('PINECONE_API_KEY'))
    print('Pinecone client created')
    try:
        # Try to import ServerlessSpec
        from pinecone import ServerlessSpec
        spec = ServerlessSpec(cloud='aws', region='us-east-1')
        print('ServerlessSpec available')
    except Exception as e:
        print('ServerlessSpec not available or import failed:', e)
        spec = None

    # Pinecone index names must be lowercase alphanumeric and '-'
    index_name = 'ayurwell'
    dim = 384
    metric = os.getenv('PINECONE_METRIC', 'cosine')

    existing = None
    try:
        existing = pc.list_indexes()
        print('Existing indexes:', existing)
    except Exception as e:
        print('pc.list_indexes failed:', e)

    if isinstance(existing, list) and index_name in existing:
        print(f"Index {index_name} already exists; skipping creation")
    else:
        try:
            if spec is not None:
                print('Creating with ServerlessSpec...')
                pc.create_index(name=index_name, dimension=dim, metric=metric, spec=spec)
            else:
                print('Creating without spec...')
                pc.create_index(name=index_name, dimension=dim, metric=metric)
            print(f"Index {index_name} created")
        except Exception as e:
            print('Failed to create index:', e)

except Exception as e:
    print('Failed to import or use pinecone client:', e)
