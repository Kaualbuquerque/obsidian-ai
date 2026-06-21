from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from config import configure_settings, get_vector_store, NOTAS_DIR, COLLECTION_NAME, DATA_DIR
import chromadb

configure_settings()

print("Limpando índice anterior...")
chroma_client = chromadb.PersistentClient(path=DATA_DIR)

try:
    chroma_client.delete_collection(COLLECTION_NAME)
    print("✓ Índice anterior removido.")
except Exception:
    print("Nenhum índice anterior encontrado, criando do zero.")

_, _, vector_store, storage_context = get_vector_store()

print("\nLendo e indexando suas notas...")
documents = SimpleDirectoryReader(NOTAS_DIR).load_data()

index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context,
    show_progress=True
)

print(f"\n✓ {len(documents)} nota(s) indexada(s) e salvas com sucesso!")
print("Agora rode 'python main.py' para conversar com a IA.")