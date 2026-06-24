from llama_index.core import VectorStoreIndex
from config import configure_settings, get_vector_store, COLLECTION_NAME

_chat_engine = None

SYSTEM_PROMPT = """Você é Obsidius, o assistente pessoal de inteligência artificial do cofre de notas do usuário.
Responda à pergunta utilizando estritamente o contexto das notas fornecidas.

Diretrizes obrigatórias:
1. Se a resposta não puder ser encontrada nas notas, diga exatamente:
   "Desculpe, não encontrei essa informação nas suas notas do Obsidian."
2. Ao final de toda resposta, liste obrigatoriamente os arquivos usados como fonte no formato:
   Fontes: [[nome-da-nota-1]], [[nome-da-nota-2]]"""


def get_chat_engine():
    global _chat_engine

    if _chat_engine is not None:
        return _chat_engine

    configure_settings()
    chroma_client, chroma_collection, vector_store, storage_context = get_vector_store()

    try:
        chroma_client.get_collection(COLLECTION_NAME)
    except Exception as e:
        print(f"Erro ao buscar coleção: {e}")
        return None

    index = VectorStoreIndex.from_vector_store(
        vector_store,
        storage_context=storage_context,
    )

    _chat_engine = index.as_chat_engine(
        chat_mode="context",
        system_prompt=SYSTEM_PROMPT,
        similarity_top_k=3,
        verbose=False
    )

    return _chat_engine


def ask(question: str) -> str:
    engine = get_chat_engine()

    if engine is None:
        return "Nenhum índice encontrado. Rode a reindexação primeiro."

    response = engine.chat(question)
    return str(response)


def reset_chat_engine():
    global _chat_engine
    _chat_engine = None