import os
import logging
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.storage.storage_context import StorageContext

load_dotenv()
logging.getLogger("httpx").setLevel(logging.WARNING)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
NOTES_DIR = "./test_notes"
DATA_DIR = "./data"
COLLECTION_NAME = "Folio_notes"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "llama-3.3-70b-versatile"
_settings_configured = False


def configure_settings():
    global _settings_configured
    if _settings_configured:
        return

    llm = Groq(model=LLM_MODEL, api_key=GROQ_API_KEY)
    embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL)
    Settings.llm = llm
    Settings.embed_model = embed_model

    _settings_configured = True


def get_vector_store():
    chroma_client = chromadb.PersistentClient(path=DATA_DIR)
    chroma_collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return chroma_client, chroma_collection, vector_store, storage_context
