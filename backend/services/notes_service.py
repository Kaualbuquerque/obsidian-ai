import re
import yaml
import chromadb
from datetime import date
from pathlib import Path

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex

import config
from config import configure_settings, get_vector_store, DATA_DIR, COLLECTION_NAME


def read_frontmatter(path: Path) -> dict:
    try:
        text = Path(path).read_text(encoding="utf-8")
        start = text.find("---")
        if start == -1:
            return {}
        end = text.find("---", start + 3)
        if end == -1:
            return {}
        raw = text[start + 3:end]
        normalized = re.sub(r':(?=\S)', ': ', raw)
        result = yaml.safe_load(normalized)
        if not isinstance(result, dict):
            return {}
        return {k.lower(): v for k, v in result.items()}
    except Exception as e:
        print(f"error reading frontmatter: {e}")
        pass
    return {}


def format_date(d: date) -> str:
    return d.strftime("%Y-%m-%d")


def note_template(title: str = "Nova nota") -> str:
    return f"""---
Tags: []
---

# {title}

"""


def analyze_notes() -> dict:
    notes_dir = Path(config.NOTES_DIR)
    files = list(notes_dir.glob("**/*.md"))

    total = len(files)
    tags_count = {}
    creation_dates = {}
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
        "orphans": orphans
    }


def reindex_notes() -> int:
    configure_settings()
    chroma_client = chromadb.PersistentClient(path=DATA_DIR)

    try:
        chroma_client.delete_collection(COLLECTION_NAME)
    except Exception as e:
        print(f"error deleting collection: {e}")

    _, _, vector_store, storage_context = get_vector_store()
    documents = SimpleDirectoryReader(config.NOTES_DIR, recursive=True).load_data()

    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
    )

    return len(documents)


def list_notes() -> list[dict]:
    notes_dir = Path(config.NOTES_DIR)
    files = list(notes_dir.glob("**/*.md"))

    notes = []
    for file in files:
        stat = file.stat()
        fm = read_frontmatter(file)

        tags = fm.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]

        notes.append({
            "title": file.stem,
            "created_at": date.fromtimestamp(stat.st_ctime).isoformat(),
            "tags": tags,
        })

    notes.sort(key=lambda x: x["created_at"], reverse=True)
    return notes


def _find_note_file(title: str) -> Path | None:
    notes_dir = Path(config.NOTES_DIR)
    matches = list(notes_dir.glob(f"**/{title}.md"))
    return matches[0] if matches else None


def get_note(title: str) -> dict | None:
    file = _find_note_file(title)
    if file is None:
        return None

    content = file.read_text(encoding="utf-8")
    frontmatter = {}
    body = content

    start = content.find("---")
    if start != -1:
        end = content.find("---", start + 3)
        if end != -1:
            raw = content[start + 3:end]
            normalized = re.sub(r':(?=\S)', ': ', raw)
            result = yaml.safe_load(normalized)
            if isinstance(result, dict):
                frontmatter = {k.lower(): v for k, v in result.items()}
            body = content[end + 3:].strip()

    return {
        "title": title,
        "content": body,
        "frontmatter": frontmatter,
        "tags": frontmatter.get("tags", []),
    }


def create_note(title: str, content: str | None = None) -> dict:
    notes_dir = Path(config.NOTES_DIR)
    file = notes_dir / f"{title}.md"

    text = content if content is not None else note_template(title)
    file.write_text(text, encoding="utf-8")

    return {"title": title, "status": "created"}


def update_note(title: str, content: str) -> dict | None:
    file = _find_note_file(title)
    if file is None:
        return None

    file.write_text(content, encoding="utf-8")
    return {"title": title, "status": "updated"}


def delete_note(title: str) -> dict | None:
    file = _find_note_file(title)
    if file is None:
        return None

    file.unlink()
    return {"title": title, "status": "deleted"}


def rename_note(old_title: str, new_title: str) -> dict | None:
    old_file = _find_note_file(old_title)
    if old_file is None:
        return None

    new_file = old_file.parent / f"{new_title}.md"
    if new_file.exists():
        return {"error": "file already exists"}

    content = old_file.read_text(encoding="utf-8")
    updated_content = re.sub(r'^#\s+.+', f'# {new_title}', content, count=1, flags=re.MULTILINE)

    new_file.write_text(updated_content, encoding="utf-8")
    old_file.unlink()

    return {"old_title": old_title, "new_title": new_title, "status": "renamed"}


def index_single_note(title: str) -> None:
    configure_settings()
    _, chroma_collection, vector_store, storage_context = get_vector_store()

    note_path = _find_note_file(title)
    if note_path is None:
        return

    document = SimpleDirectoryReader(input_files=[str(note_path)]).load_data()[0]

    try:
        chroma_collection.delete(where={"file_name": f"{title}.md"})
    except Exception as e:
        print(f"error deleting collection: {e}")

    index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)
    index.insert(document)


def remove_note_from_index(title: str) -> None:
    configure_settings()
    _, chroma_collection, _, _ = get_vector_store()

    try:
        chroma_collection.delete(where={"file_name": f"{title}.md"})
    except Exception as e:
        print(f"error deleting collection: {e}")
