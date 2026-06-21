from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.storage.storage_context import StorageContext
from config import configure_settings, COLLECTION_NAME, DATA_DIR
import chromadb

configure_settings()

# ── Carregar índice existente do ChromaDB
chroma_client = chromadb.PersistentClient(path=DATA_DIR)

try:
    chroma_collection = chroma_client.get_collection(COLLECTION_NAME)
except Exception:
    print("Nenhum índice encontrado.")
    print("Rode primeiro: python indexer.py")
    exit()

vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_vector_store(
    vector_store,
    storage_context=storage_context
)

total_notas = chroma_collection.count()
print(f"✓ Índice carregado — {total_notas} chunk(s) indexado(s).\n")

# ── Motor de consulta
SYSTEM_PROMPT = """Você é o assistente pessoal de inteligência artificial do cofre de notas do usuário.
Responda à pergunta utilizando estritamente o contexto das notas fornecidas.

Diretrizes obrigatórias:
1. Se a resposta não puder ser encontrada nas notas, diga exatamente:
   "Desculpe, não encontrei essa informação nas suas notas do Obsidian."
2. Ao final de toda resposta, liste obrigatoriamente os arquivos usados como fonte no formato:
   Fontes: [[nome-da-nota-1]], [[nome-da-nota-2]]"""

chat_engine = index.as_chat_engine(
    chat_mode="context",
    system_prompt=SYSTEM_PROMPT,
    similarity_top_k=3,
    verbose=False
)

# ── Loop de chat
print("=" * 50)
print("Obsidian AI — Digite 'sair' para encerrar")
print("=" * 50)

while True:
    pergunta = input("\nVocê: ").strip()

    if not pergunta:
        continue

    if pergunta.lower() in ["sair", "exit", "quit"]:
        print("Encerrando...")
        break

    print("\nIA: Buscando nas suas notas...\n")
    resposta = chat_engine.chat(pergunta)
    print(f"IA: {resposta}\n")
    print("-" * 50)
