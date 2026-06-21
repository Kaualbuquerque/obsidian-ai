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
from config import configure_settings, get_vector_store, COLLECTION_NAME, DATA_DIR, NOTES_DIR
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

    /* Header */
    [data-testid="stHeader"] {
    background-color: var(--bg);
    border-bottom: 1px solid var(--border);
    }

    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 2px; }

    /* Sidebar */
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

    /* stats */
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

    /* Tag */
    .tag-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 7px 10px;
        border-radius: 8px;
        margin-bottom: 5px;
        background: var(--card);
        border: 1px solid var(--border);
    }
    .tag-name {
        font-size: 13px;
        color: var(--primary-glow);
    }
    .tag-count {
        font-size: 11px;
        background: var(--accent);
        color: var(--primary-glow);
        border-radius: 20px;
        padding: 1px 8px;
    }
    
    /* Calendário */
    .cal-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 2px;
    }
    .cal-day-name {
        text-align: center;
        font-size: 10px;
        color: var(--muted);
        padding: 3px;
        text-transform: uppercase;
    }
    .cal-day {
        text-align: center;
        font-size: 11px;
        padding: 5px 2px;
        border-radius: 4px;
        color: var(--muted);
        position: relative;
    }
    .cal-day.has-notes {
        color: var(--text);
        background: var(--card);
        border: 1px solid var(--border);
    }
    .cal-day.has-compromisso::after {
        content: "";
        position: absolute;
        bottom: 2px;
        left: 50%;
        transform: translateX(-50%);
        width: 4px;
        height: 4px;
        border-radius: 50%;
        background: #f59e0b;
    }
    .cal-day.today {
        border: 1px solid var(--primary);
        color: var(--primary-glow);
        font-weight: 600;
    }
    .cal-day.selected {
        background: var(--primary);
        color: white;
        border: none;
    }
    .cal-day.empty {
        color: transparent;
    }
    
    /* Card */
    .nota-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 8px 10px;
        margin-bottom: 6px;
    }
    .nota-card-titulo {
        font-size: 12px;
        font-weight: 500;
        color: var(--text);
    }
    .nota-card-data {
        font-size: 11px;
        color: var(--muted);
        margin-top: 2px;
    }
    .notas-scroll {
        max-height: 180px;
        overflow-y: auto;
        padding-right: 4px;
        margin-top: 6px;
    }
    
    /* Chat */
    .chat-header {
        border-bottom: 1px solid var(--border);
        padding-bottom: 14px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .chat-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 18px;
        font-weight: 600;
        color: var(--text);
    }
    .chat-subtitle {
        font-size: 12px;
        color: var(--muted);
        margin-top: 2px;
    }
    
    /* Remetente */
    .msg-user {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 16px;
    }
    .msg-ia {
        display: flex;
        justify-content: flex-start;
        margin-bottom: 16px;
    }
    
    /* Balão de mensagem */
    .bubble-user {
        background: var(--primary);
        color: white;
        padding: 10px 16px;
        border-radius: 18px 18px 4px 18px;
        max-width: 70%;
        font-size: 14px;
        line-height: 1.6;
        white-space: pre-wrap;
    }
    .bubble-ia {
        background: var(--card);
        color: var(--text);
        padding: 12px 16px;
        border: 1px solid var(--border);
        border-radius: 18px 18px 18px 4px;
        max-width: 75%;
        font-size: 14px;
        line-height: 1.6;
        white-space: pre-wrap;
    }
    .sender-label {
        font-size: 11px;
        color: var(--muted);
        margin-bottom: 4px;
    }
    
    /* Hero */
    .welcome-container {
        text-align: center;
        padding: 4rem 0;
    }
    .welcome-icon {
        font-size: 52px;
        margin-bottom: 1rem;
    }
    .welcome-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 24px;
        font-weight: 600;
        color: var(--text);
        margin-bottom: 8px;
    }
    .welcome-title span {
        color: var(--primary-glow);
    }
    .welcome-subtitle {
        font-size: 14px;
        color: var(--muted);
        margin-bottom: 2rem;
    }
    
    /* Sugestão de pergunta */
    .suggestion-grid {
        display: flex;
        gap: 10px;
        justify-content: center;
        flex-wrap: wrap;
    }
    .suggestion-chip {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 8px 16px;
        font-size: 13px;
        color: var(--muted);
        cursor: pointer;
        transition: border-color 0.15s;
    }
    .suggestion-chip:hover {
        border-color: var(--primary);
        color: var(--text);
    }
</style>
""", unsafe_allow_html=True)


#  ── Funções auxiliares
def read_frontmatter(path):
    try:
        text = Path(path).read_text(encoding="utf-8")
        if text.startswith("---"):
            end = text.find("---", 3)
            if end != -1:
                return yaml.safe_load(text[3:end]) or {}
    except Exception:
        pass
    return {}


def analyze_notes():
    notes_dir = Path(NOTES_DIR)
    files = list(notes_dir.glob("**/*.md"))

    total = len(files)
    tags_count = {}
    creation_dates = {}
    events = {}
    received_links = {f.stem: 0 for f in files}

    for file in files:
        fm = read_frontmatter(file)

        tags = fm.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        for tag in tags:
            tags_count[tag] = tags_count.get(tag, 0) + 1

        stat = file.stat()
        creation_date = date.fromtimestamp(stat.st_ctime)
        creation_dates[file.stem] = creation_date

        if fm.get("compromisso"):
            events[creation_date] = fm.get("compromisso")

        text = file.read_text(encoding="utf-8", errors="ignore")
        links = re.findall(r'\[\[([^\]]+)\]\]', text)
        for link in links:
            clean_link = link.split("|")[0].strip()
            if clean_link in received_links:
                received_links[clean_link] += 1

    orphans = sum(1 for v in received_links.values() if v == 0)

    return {
        "total": total,
        "tags": dict(sorted(tags_count.items(), key=lambda x: x[1], reverse=True)),
        "creation_dates": creation_dates,
        "events": events,
        "orphans": orphans
    }


def generate_calendar(year, month, dates_with_notes, events, selected_day=None):
    today = date.today()
    cal = calendar.monthcalendar(year, month)
    weekdays = ["S", "T", "Q", "Q", "S", "S", "D"]

    html = ""
    html += '<div class="cal-grid">'

    for d in weekdays:
        html += f'<div class="cal-day-name">{d}</div>'

    for week in cal:
        for day in week:
            if day == 0:
                html += '<div class="cal-day empty">·</div>'
            else:
                current_date = date(year, month, day)
                classes = ["cal-day"]
                if current_date in dates_with_notes:
                    classes.append("has-notes")
                if current_date in events:
                    classes.append("has-compromisso")
                if current_date == today:
                    classes.append("today")
                if selected_day and current_date == selected_day:
                    classes.append("selected")
                html += f'<div class="{" ".join(classes)}">{day}</div>'

    html += '</div>'
    return html


#  ── Carregamento da IA e session state
@st.cache_resource
def load_engine():
    configure_settings()
    try:
        chroma_client, chroma_collection, vector_store, storage_context = get_vector_store()
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


if "history" not in st.session_state:
    st.session_state["history"] = []

if "current_month" not in st.session_state:
    st.session_state["current_month"] = date.today().month

if "current_year" not in st.session_state:
    st.session_state["current_year"] = date.today().year

if "selected_day" not in st.session_state:
    st.session_state["selected_day"] = None

if "reindex" not in st.session_state:
    st.session_state["reindex"] = False


#  ── Watchdog
class NotesMonitor(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.src_path.endswith(".md"):
            st.session_state["reindex"] = True


def start_watchdog():
    if "watchdog_active" not in st.session_state:
        handler = NotesMonitor()
        observer = Observer()
        observer.schedule(handler, path=NOTES_DIR, recursive=True)
        observer.start()
        st.session_state["watchdog_active"] = True


# TODO: Fase Electron — migrar para sistema de eventos independente
def reindex_notes():
    configure_settings()
    chroma_client = chromadb.PersistentClient(path=DATA_DIR)
    try:
        chroma_client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    _, _, vector_store, storage_context = get_vector_store()
    documents = SimpleDirectoryReader(NOTES_DIR).load_data()
    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context
    )
    st.cache_resource.clear()


# ── Inicialização
start_watchdog()

if st.session_state["reindex"]:
    with st.spinner("Novas notas detectadas, reindexando..."):
        reindex_notes()
    st.session_state["reindex"] = False
    st.rerun()

data = analyze_notes()
collection, chat_engine = load_engine()


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
    st.markdown('<div class="section-label">Visão geral</div>',
                unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Notas</div>
            <div class="stat-value">{data['total']}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Órfãs</div>
            <div class="stat-value">{data['orphans']}</div>
        </div>
        """, unsafe_allow_html=True)

    # Tags
    st.markdown('<div class="section-label">Tags</div>',
                unsafe_allow_html=True)
    if data["tags"]:
        for tag, count in list(data["tags"].items())[:8]:
            st.markdown(f"""
                        <div class="tag-item">
                            <span class="tag-name">#{tag}<span>
                            <span class="tag-count">#{count}<span>
                        </div>
                        """, unsafe_allow_html=True)
    else:
        st.markdown("""
                    <div style='font-size:12px; color:var(--muted);'>
                        Nenhuma tag encontrada.
                    </div>
                    """, unsafe_allow_html=True)

    # Calendário
    st.markdown('<div class="section-label">Calendário</div>',
                unsafe_allow_html=True)

    nav1, nav2, nav3 = st.columns([1, 3, 1])
    with nav1:
        if st.button("‹", key="prev_month"):
            if st.session_state["current_month"] == 1:
                st.session_state["current_month"] = 12
                st.session_state["current_year"] -= 1
            else:
                st.session_state["current_month"] -= 1

    with nav2:
        month_names = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março",    4: "Abril",
            5: "Maio",    6: "Junho",     7: "Julho",     8: "Agosto",
            9: "Setembro", 10: "Outubro",  11: "Novembro", 12: "Dezembro"
        }

        st.markdown(f"""
                    <div style='text-align:center; font-size:12px; font-weight:600;
                                color:var(--primary-glow); padding-top:6px;'>
                        {month_names[st.session_state['current_month']]} {st.session_state['current_year']}
                    </div>
                    """, unsafe_allow_html=True)

    with nav3:
        if st.button("›", key="next_month"):
            if st.session_state["current_month"] == 12:
                st.session_state["current_month"] = 1
                st.session_state["current_year"] += 1
            else:
                st.session_state["current_month"] += 1

    dates_with_notes = set(data["creation_dates"].values())

    calendar_html = generate_calendar(
        st.session_state["current_year"],
        st.session_state["current_month"],
        dates_with_notes,
        data["events"],
        st.session_state["selected_day"],
    )

    st.markdown(calendar_html, unsafe_allow_html=True)

    # Filtro por dia
    st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)

    current_month = st.session_state["current_month"]
    current_year = st.session_state["current_year"]
    _, total_days = calendar.monthrange(current_year, current_month)

    options = ["Selecione um dia"] + [str(d) for d in range(1, total_days + 1)]
    chosen_day = st.selectbox(
        "Filtrar por dia",
        options,
        label_visibility="collapsed"
    )

    if chosen_day != "Selecione um dia...":
        try:
            st.session_state["selected_day"] = date(
                current_year,
                current_month,
                int(chosen_day)
            )
        except Exception:
            st.session_state["selected_day"] = None
    else:
        st.session_state["selected_day"] = None

    # Notas do dia selecionado
    if st.session_state["selected_day"]:
        selected_date = st.session_state["selected_day"]
        notes_of_day = [n for n, d in data["creation_dates"].items()
                        if d == selected_date]

        event_of_day = data["events"].get(selected_date)
        if event_of_day:
            st.markdown(f"""
            <div style='font-size:12px; color:#f59e0b; margin-top:6px;'>
                🗓 {event_of_day}
            </div>
            """, unsafe_allow_html=True)

        if notes_of_day:
            st.markdown(f"""
            <div style='font-size:11px; color:var(--muted); margin-top:8px;'>
                {len(notes_of_day)} nota(s) em {selected_date.strftime('%d/%m/%Y')}
            </div>
            """, unsafe_allow_html=True)

            cards_html = '<div class="notes-scroll">'
            for note in notes_of_day:
                formatted_date = selected_date.strftime('%d/%m/%Y')
                cards_html += f'<div class="note-card">'
                cards_html += f'<div class="note-card-title">📄 {note}</div>'
                cards_html += f'<div class="note-card-date">{formatted_date}</div>'
                cards_html += f'</div>'
            cards_html += '</div>'
            st.markdown(cards_html, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='font-size:12px; color:var(--muted); margin-top:8px;'>
                Nenhuma nota criada nesse dia.
            </div>
            """, unsafe_allow_html=True)

    # Reindexar
    st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Índice</div>',
                unsafe_allow_html=True)
    if st.button("🔄 Reindexar notas", use_container_width=True):
        with st.spinner("Reindexando..."):
            reindex_notes()
        st.success("Notas reindexadas com sucesso!")
        st.rerun()

# ── Chat
col_header1, col_header2 = st.columns([6, 1])
with col_header1:
    st.markdown("""
    <div class="chat-header">
        <div>
            <div class="chat-title">Conversa</div>
            <div class="chat-subtitle">A IA busca respostas nas suas notas.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_header2:
    if st.button("Limpar", key="clear_chat"):
        st.session_state["history"] = []
        if chat_engine:
            chat_engine.reset()
        st.rerun()

# Tela de boas vindas ou histórico
if collection is None:
    st.markdown("""
    <div class="welcome-container">
        <div class="welcome-icon">🟣</div>
        <div class="welcome-title">Nenhum índice encontrado</div>
        <div class="welcome-subtitle">
            Clique em "Reindexar notas" no sidebar para começar.
        </div>
    </div>
    """, unsafe_allow_html=True)

elif not st.session_state["history"]:
    st.markdown("""
    <div class="welcome-container">
        <div class="welcome-icon">🟣</div>          
        <div class="welcome-title">
            Olá! Eu sou o <span>Obsidius.</span>
        </div>
        <div class="welcome-subtitle">
            Pergunte sobre suas notas ou peça sugestões.
        </div>
        <div class="suggestion-grid">
            <div class="suggestion-chip">📄 Liste minhas notas mais recentes</div>
            <div class="suggestion-chip">🔍 O que tenho sobre produtividade?</div>
            <div class="suggestion-chip">💡 Quais são minhas ideias principais?</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    for msg in st.session_state["history"]:
        if msg["role"] == "user":
            st.markdown(f"""
                <div class="msg-user">
                    <div>
                        <div class="sender-label" style="text-align:right;">Você</div>
                        <div class="bubble-user">{msg["content"]}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="msg-ai">
                    <div>
                        <div class="sender-label">Obsidius</div>
                        <div class="bubble-ai">{msg["content"]}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# Input do chat
if collection is not None:
    question = st.chat_input("Pergunte algo sobre suas notas...")
    if question and chat_engine:
        st.session_state["history"].append(
            {"role": "user", "content": question})
        with st.spinner("Buscando nas suas notas..."):
            answer = chat_engine.chat(question)
        st.session_state["history"].append({
            "role": "assistant",
            "content": str(answer)
        })
        st.rerun()
