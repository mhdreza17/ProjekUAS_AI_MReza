import os
import chromadb

os.environ['ANONYMIZED_TELEMETRY'] = 'False'
os.environ['CHROMA_CLIENT_AUTH_PROVIDER'] = ''
os.environ['CHROMA_SERVER_NOFILE'] = '1'
os.environ['CHROMA_SERVER_CORS_ALLOW_ORIGINS'] = '[]'

try:
    import chromadb.telemetry.product.posthog
    chromadb.telemetry.product.posthog.Posthog = lambda *args, **kwargs: None
except:
    pass

def get_chromadb_client(path="vector_db"):
    """Get ChromaDB client with telemetry disabled"""
    try:
        settings = chromadb.config.Settings(
            anonymized_telemetry=False,
            allow_reset=True
        )
        return chromadb.PersistentClient(path=path, settings=settings)
    except Exception as e:
        # Fallback without settings if there's an issue
        return chromadb.PersistentClient(path=path)
