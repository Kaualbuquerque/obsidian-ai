import streamlit as st
import os
import re
import calendar
from datetime import date
from pathlib import Path
import yaml
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from config import configurar_settings, obter_vector_store, COLLECTION_NAME, DATA_DIR, NOTAS_DIR
import chromadb
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# ── Configuração da página
st.set_page_config(
    page_title="Obsidius",
    page_icon="🟣",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ── Estilos visuais
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600&family=Inter:wght@400;500&display=swap');

:root {
    --bg:           #1a1425;
    --sidebar:      #15101f;
    --card:         #201e30;
    --primary:      #7c5cfc;
    --primary-glow: #a38bff;
    --accent:       #4b3a6b;
    --border:       #3a3550;
    --muted:        #9e94b8;
    --destructive:  #e8546b;
    --text:         #e0e0f0;
}

.stApp {
    background-color: var(--bg);
    font-family: 'Inter', sans-serif;
    color: var(--text);
}

#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }

[data-testid="stDecoration"] { visibility: hidden; }
[data-testid="stStatusWidget"] { visibility: hidden; }

[data-testid="stHeader"] {
    background-color: var(--bg);
    border-bottom: 1px solid var(--border);
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 2px; }

section[data-testid="stSidebar"] {
        background-color: var(--sidebar);
        border-right: 1px solid var(--border);
    }
section[data-testid="stSidebar"] * {
        color: var(--text) !important;
    }
    
.sidebar-header {
        padding: 0.5rem 0 1rem;
        border-bottom: 1px solid var(--border);
        margin-bottom: 16px;
    }   
.sidebar-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 20px;
        font-weight: 600;
        color: var(--primary-glow);
    }  
.sidebar-subtitle {
        font-size: 12px;
        color: var(--muted);
        margin-top: 2px;
    }   
.section-label {
        font-size: 10px;
        font-weight: 600;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin: 14px 0 8px;
    }  
    
.stat-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 10px;
    }
.stat-label {
        font-size: 11px;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
.stat-value {
        font-size: 26px;
        font-weight: 600;
        font-family: 'Space Grotesk', sans-serif;
        color: var(--primary-glow);
    }
</style>
""", unsafe_allow_html=True)


#  ── Funções auxiliares
def ler_fontmatter(caminho):
    try:
        texto = Path(caminho).read_text(encoding="utf-8")
        if texto.startswith("---"):
            fim = texto.find("---", 3)
            if fim != -1:
                return yaml.safe_load(texto[3:fim]) or {}
    except Exception:
        pass
    return {}


def analisar_notas():
    notas_dir = Path(NOTAS_DIR)
    arquivos = list(notas_dir.glob("**/*.md"))

    total = len(arquivos)
    tags_contagem = {}
    datas_criacao = {}
    compromissos = {}
    links_recebidos = {a.stem: 0 for a in arquivos}

    for arq in arquivos:
        fm = ler_fontmatter(arq)

        tags = fm.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        for tag in tags:
            tags_contagem[tag] = tags_contagem.get(tag, 0) + 1

        stat = arq.stat()
        data_criacao = date.fromtimestamp(stat.st_ctime)
        datas_criacao[arq.stem] = data_criacao

        if fm.get("compromisso"):
            compromissos[data_criacao] = fm.get("compromisso")

        texto = arq.read_text(encoding="utf-8", errors="ignore")
        links = re.findall(r'\[\[([^\]]+)\]\]', texto)
        for link in links:
            link_limpo = link.split("|")[0].strip()
            if link_limpo in links_recebidos:
                links_recebidos[link_limpo] += 1

    orfas = sum(1 for v in links_recebidos.values() if v == 0)

    return {
        "total": total,
        "tags": dict(sorted(tags_contagem.items(), key=lambda x: x[1], reverse=True)),
        "datas_criacao": datas_criacao,
        "compromissos": compromissos,
        "orfas": orfas
    }


def gerar_calendario(ano, mes, datas_com_notas, compromissos, dia_selecionado=None):
    hoje = date.today()
    nomes_mes = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março",    4: "Abril",
        5: "Maio",    6: "Junho",     7: "Julho",     8: "Agosto",
        9: "Setembro", 10: "Outubro",  11: "Novembro", 12: "Dezembro"
    }

    cal = calendar.monthcalendar(ano, mes)
    dias_semana = ["S", "T", "Q", "Q", "S", "S", "D"]

    html = f'<div class="cal-header">{nomes_mes[mes]} {ano}</div>'
    html += '<div class="cal-grid">'

    for d in dias_semana:
        html += f'<div class="cal-day-name">{d}</div>'

    for semana in cal:
        for dia in semana:
            if dia == 0:
                html += '<div class="cal-day empty">·</div>'
            else:
                data_atual = date(ano, mes, dia)
                classes = ["cal-day"]
                if data_atual in datas_com_notas:
                    classes.append("has-notes")
                if data_atual in compromissos:
                    classes.append("has-compromisso")
                if data_atual == hoje:
                    classes.append("today")
                if dia_selecionado and data_atual == dia_selecionado:
                    classes.append("selected")
                html += f'<div class="{" ".join(classes)}">{dia}</div>'

    html += '</div>'
    return html


#  ── Carregamento da IA e session state
@st.cache_resource
def carregar_engine():
    configurar_settings()
    try:
        chroma_client, chroma_collection, vector_store, storage_context = obter_vector_store()
        chroma_client.get_collection(COLLECTION_NAME)
    except Exception:
        return None, None

    index = VectorStoreIndex.from_vector_store(
        vector_store,
        storage_context=storage_context
    )

    SYSTEM_PROMPT = """Você é Obsidius, o assistente pessoal de inteligência artificial do cofre de notas do usuário.
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

    return chroma_collection, chat_engine


if "historico" not in st.session_state:
    st.session_state["historico"] = []

if "mes_atual" not in st.session_state:
    st.session_state["mes_atual"] = date.today().month

if "ano_atual" not in st.session_state:
    st.session_state["ano_atual"] = date.today().year

if "dia_selecionado" not in st.session_state:
    st.session_state["dia_selecionado"] = None

if "reindexar" not in st.session_state:
    st.session_state["reindexar"] = False


#  ── Watchdog
class MonitorNotas(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.src_path.endswith(".md"):
            st.session_state["reindexar"] = True


def iniciar_watchdog():
    if "watchdog_ativo" not in st.session_state:
        handler = MonitorNotas()
        observer = Observer()
        observer.schedule(handler, path=NOTAS_DIR, recursive=True)
        observer.start()
        st.session_state["watchdog_ativo"] = True


# TODO: Fase Electron — migrar para sistema de eventos independente
def reindexar_notas():
    configurar_settings()
    chroma_client = chromadb.PersistentClient(path=DATA_DIR)
    try:
        chroma_client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    _, _, vector_store, storage_context = obter_vector_store()
    documents = SimpleDirectoryReader(NOTAS_DIR).load_data()
    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context
    )
    st.cache_resource.clear()


# ── Inicialização
iniciar_watchdog()

if st.session_state["reindexar"]:
    with st.spinner("Novas notas detectadas, reindexando..."):
        reindexar_notas()
    st.session_state["reindexar"] = False
    st.rerun()

dados = analisar_notas()
colecao, chat_engine = carregar_engine()


# ── Sidebar
with st.sidebar:
    # Header
    st.markdown(f"""
    <div class="sidebar-header">
        <div class="sidebar-title">🟣 Obsidius</div>
        <div class="sidebar-subtitle">IA para suas notas</div>
    </div>
    """, unsafe_allow_html=True)

    # Cards de estatísticas
    st.markdown('<div class="section-label">Visão geral</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Notas</div>
            <div class="stat-value">{dados['total']}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Órfãs</div>
            <div class="stat-value">{dados['orfas']}</div>
        </div>
        """, unsafe_allow_html=True)
