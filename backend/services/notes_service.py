import re
import yaml
import chromadb
from datetime import date
from pathlib import Path

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex

from config import configure_settings, get_vector_store, NOTES_DIR, DATA_DIR, COLLECTION_NAME


def read_fontmatter(path: Path) -> dict:
    try:
        text = Path(path).read_text(encoding="utf-8")
        if text.startswith("---"):
            end = text.find("---", 3)
            if end != -1:
                return yaml.safe_load(text[3:end]) or {}
    except Exception as e:
        print(f"Erro ao buscar fontmatter: {e}")
        pass
    return {}


def analyze_notes() -> dict:
    notes_dir = Path(NOTES_DIR)
    files = list(notes_dir.glob("**/*.md"))

    total = len(files)
    tags_count = {}
    creation_dates = {}
    events = {}
    received_links = {f.stem: 0 for f in files}

    for file in files:
        fm = read_fontmatter(file)

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


def reindex_notes() -> int:
    configure_settings()
    chroma_client = chromadb.PersistentClient(path=DATA_DIR)

    try:
        chroma_client.delete_collection(COLLECTION_NAME)
    except Exception as e:
        print(f"Erro ao deletar collection: {e}")
        pass

    _, _, vector_store, storage_context = get_vector_store()
    documents = SimpleDirectoryReader(NOTES_DIR).load_data()

    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
    )

    return len(documents)
