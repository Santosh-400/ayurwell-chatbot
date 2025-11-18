from dotenv import load_dotenv
import os
load_dotenv()
print('PINECONE_API_KEY set:', bool(os.getenv('PINECONE_API_KEY')))
try:
    import pinecone
    print('pinecone module imported, version:', getattr(pinecone, '__version__', 'n/a'))
    print('has init:', hasattr(pinecone, 'init'))
    print('has Pinecone class:', hasattr(pinecone, 'Pinecone'))
    print('has create_index at top level:', hasattr(pinecone, 'create_index'))
    # Try old list_indexes
    try:
        if hasattr(pinecone, 'init'):
            try:
                pinecone.init(api_key=os.getenv('PINECONE_API_KEY'), environment=os.getenv('PINECONE_ENVIRONMENT') or os.getenv('PINECONE_REGION'))
            except Exception as e:
                print('pinecone.init failed:', e)
            try:
                print('pinecone.list_indexes():', pinecone.list_indexes())
            except Exception as e:
                print('pinecone.list_indexes() failed:', e)
        if hasattr(pinecone, 'Pinecone'):
            try:
                pc = pinecone.Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
            except Exception as e:
                print('pinecone.Pinecone(...) instantiation failed:', e)
                pc = None
            if pc:
                try:
                    li = pc.list_indexes()
                    print('pc.list_indexes():', li)
                except Exception as e:
                    print('pc.list_indexes() failed:', e)
                # Try to describe known index
                try:
                    if 'healthguru' in (li if isinstance(li, list) else []):
                        print('Describing index healthguru...')
                        try:
                            desc = pc.describe_index('healthguru')
                            print('describe_index result:', desc)
                        except Exception as e:
                            print('pc.describe_index failed:', e)
                except Exception as e:
                    print('Error during index describe step:', e)
    except Exception as e:
        print('Error exploring pinecone client:', e)
except Exception as e:
    print('Failed to import pinecone:', e)
