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
    cal = calendar.monthcalendar(ano, mes)
    dias_semana = ["S", "T", "Q", "Q", "S", "S", "D"]

    html = ""
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
    st.markdown('<div class="section-label">Visão geral</div>',
                unsafe_allow_html=True)
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

    # Tags
    st.markdown('<div class="section-label">Tags</div>',
                unsafe_allow_html=True)
    if dados["tags"]:
        for tag, qtd in list(dados["tags"].items())[:8]:
            st.markdown(f"""
                        <div class="tag-item">
                            <span class="tag-name">#{tag}<span>
                            <span class="tag-count">#{qtd}<span>
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
        if st.button("‹", key="mes_ant"):
            if st.session_state["mes_atual"] == 1:
                st.session_state["mes_atual"] = 12
                st.session_state["ano_atual"] -= 1
            else:
                st.session_state["mes_atual"] -= 1

    with nav2:
        nomes_mes = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março",    4: "Abril",
            5: "Maio",    6: "Junho",     7: "Julho",     8: "Agosto",
            9: "Setembro", 10: "Outubro",  11: "Novembro", 12: "Dezembro"
        }

        st.markdown(f"""
                    <div style='text-align:center; font-size:12px; font-weight:600;
                                color:var(--primary-glow); padding-top:6px;'>
                        {nomes_mes[st.session_state['mes_atual']]} {st.session_state['ano_atual']}
                    </div>
                    """, unsafe_allow_html=True)

    with nav3:
        if st.button("›", key="mes_prox"):
            if st.session_state["mes_atual"] == 12:
                st.session_state["mes_atual"] = 1
                st.session_state["ano_atual"] += 1
            else:
                st.session_state["mes_atual"] += 1

    datas_com_notas = set(dados["datas_criacao"].values())

    cal_html = gerar_calendario(
        st.session_state["ano_atual"],
        st.session_state["mes_atual"],
        datas_com_notas,
        dados["compromissos"],
        st.session_state["dia_selecionado"],
    )

    st.markdown(cal_html, unsafe_allow_html=True)

    # Filtro por dia
    st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)

    mes_atual = st.session_state["mes_atual"]
    ano_atual = st.session_state["ano_atual"]
    _, total_dias = calendar.monthrange(ano_atual, mes_atual)

    opcoes = ["Selecione um dia"] + [str(d) for d in range(1, total_dias + 1)]
    dia_escolhido = st.selectbox(
        "Filtrar por dia",
        opcoes,
        label_visibility="collapsed"
    )

    if dia_escolhido != "Selecione um dia...":
        try:
            st.session_state["dia_selecionado"] = date(
                ano_atual,
                mes_atual,
                int(dia_escolhido)
            )
        except Exception:
            st.session_state["dia_selecionado"] = None
    else:
        st.session_state["dia_selecionado"] = None

    # Notas do dia selecionado
    if st.session_state["dia_selecionado"]:
        dia_sel = st.session_state["dia_selecionado"]
        notas_dia = [n for n, d in dados["datas_criacao"].items()
                     if d == dia_sel]

        compromisso_dia = dados["compromissos"].get(dia_sel)
        if compromisso_dia:
            st.markdown(f"""
            <div style='font-size:12px; color:#f59e0b; margin-top:6px;'>
                🗓 {compromisso_dia}
            </div>
            """, unsafe_allow_html=True)

        if notas_dia:
            st.markdown(f"""
            <div style='font-size:11px; color:var(--muted); margin-top:8px;'>
                {len(notas_dia)} nota(s) em {dia_sel.strftime('%d/%m/%Y')}
            </div>
            """, unsafe_allow_html=True)

            cards_html = '<div class="notas-scroll">'
            for nota in notas_dia:
                data_formatada = dia_sel.strftime('%d/%m/%Y')
                cards_html += f'<div class="nota-card">'
                cards_html += f'<div class="nota-card-titulo">📄 {nota}</div>'
                cards_html += f'<div class="nota-card-data">{data_formatada}</div>'
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
            reindexar_notas()
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
    if st.button("Limpar", key="limpar_chat"):
        st.session_state["historico"] = []
        if chat_engine:
            chat_engine.reset()
        st.rerun()

# Tela de boas vindas ou histórico
if colecao is None:
    st.markdown("""
    <div class="welcome-container">
        <div class="welcome-icon">🟣</div>
        <div class="welcome-title">Nenhum índice encontrado</div>
        <div class="welcome-subtitle">
            Clique em "Reindexar notas" no sidebar para começar.
        </div>
    </div>
    """, unsafe_allow_html=True)

elif not st.session_state["historico"]:
    st.markdown("""
    <div class="welcome-container">
        <div class="welcome-icon">🟣</div>          
        <div class="welcome-title">
            Olá! Eu sou o <span>Obsidius.</span>
        </div>
        <div class="welcome-subtitle">
            Pergunter sobre suas notas ou peça sugestões.
        </div>
        <div class="suggestion-grid">
            <div class="suggestion-chip">📄 Liste minhas notas mais recentes</div>
            <div class="suggestion-chip">🔍 O que tenho sobre produtividade?</div>
            <div class="suggestion-chip">💡 Quais são minhas ideias principais?</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
        for msg in st.session_state["historico"]:
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
                <div class="msg-ia">
                    <div>
                        <div class="sender-label">Obsidius</div>
                        <div class="bubble-ia">{msg["content"]}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# Input do chat
if colecao is not None:
    pergunta = st.chat_input("Pergunte algo sobre suas notas...")
    if pergunta and chat_engine:
        st.session_state["historico"].append({"role": "user", "content":pergunta})
        with st.spinner("Buscando nas suas notas..."):
            resposta = chat_engine.chat(pergunta)
        st.session_state["historico"].append({
            "role": "assistant",
            "content": str(resposta)
        })
        st.rerun()