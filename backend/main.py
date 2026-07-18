from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware

from config import NOTES_DIR, configure_settings
from monitor import start_watchdog, stop_watchdog
from schemas import ChatRequest, NoteCreateRequest, NoteUpdateRequest, NoteRenameRequest
from services.chat_service import ask, reset_chat_engine
from services.notes_service import analyze_notes, reindex_notes, list_notes, get_note, create_note, update_note, \
    delete_note, rename_note, index_single_note, remove_note_from_index


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_settings()
    start_watchdog()
    yield
    stop_watchdog()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "API running"}


@app.get("/notes/stats")
def get_notes_stats():
    data = analyze_notes()
    return {
        "total": data["total"],
        "orphans": data["orphans"],
        "tags": data["tags"],
    }


@app.get("/notes/calendar")
def get_notes_calendar():
    data = analyze_notes()

    dates = {
        note: creation_date.isoformat()
        for note, creation_date in data["creation_dates"].items()
    }

    events = {
        event_date.isoformat(): description
        for event_date, description in data["events"].items()
    }

    return {
        "dates": dates,
        "events": events
    }


@app.post("/chat")
def post_chat(request: ChatRequest):
    answer = ask(request.question)
    return {"answer": answer}


@app.post("/reindex")
def post_reindex():
    total = reindex_notes()
    reset_chat_engine()
    return {
        "status": "Success",
        "total_indexed": total,
    }


@app.get("/notes")
def get_notes():
    return list_notes()


@app.get("/notes/{title}")
def get_note_by_title(title: str):
    note = get_note(title)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    return note


@app.post("/notes")
def create_note_route(request: NoteCreateRequest):
    result = create_note(request.title, request.content)
    index_single_note(request.title)
    reset_chat_engine()
    return result


@app.put("/notes/{title}")
def update_note_by_title(title: str, request: NoteUpdateRequest):
    result = update_note(title, request.content)
    if result is None:
        raise HTTPException(status_code=404, detail="Note not found")
    index_single_note(title)
    reset_chat_engine()
    return result


@app.delete("/notes/{title}")
def delete_note_by_title(title: str):
    result = delete_note(title)
    if result is None:
        raise HTTPException(status_code=404, detail="Note not found")
    remove_note_from_index(title)
    reset_chat_engine()
    return result


@app.patch("/notes/{title}/rename")
def rename_note_by_title(title: str, request: NoteRenameRequest):
    result = rename_note(title, request.new_title)

    if result is None:
        raise HTTPException(status_code=404, detail="Note not found")
    if "error" in result:
        raise HTTPException(status_code=409, detail=result["error"])

    remove_note_from_index(title)
    index_single_note(request.new_title)
    reset_chat_engine()
    return result


@app.get("/vault/name")
def get_vault_name():
    return {"name": Path(NOTES_DIR).resolve().name}
