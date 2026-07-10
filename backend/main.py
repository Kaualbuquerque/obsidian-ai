from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware

from schemas import ChatRequest, NoteCreateRequest, NoteUpdateRequest, NoteRenameRequest
from services.chat_service import ask, reset_chat_engine
from services.notes_service import analyze_notes, reindex_notes, list_notes, get_note, create_note, update_note, \
    delete_note, rename_note

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "Obsidius API rodando"}


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
        raise HTTPException(status_code=404, detail="Nota não encotontrada")

    return note


@app.post("/notes")
def post_notes(request: NoteCreateRequest):
    return create_note(request.title, request.content)


@app.put("/notes/{title}")
def update_note_by_title(title: str, request: NoteUpdateRequest):
    result = update_note(title, request.content)
    if result is None:
        raise HTTPException(status_code=404, detail="Nota não encontrada")
    return result


@app.delete("/notes/{title}")
def delete_note_by_title(title: str):
    result = delete_note(title)
    if result is None:
        raise HTTPException(status_code=404, detail="Nota não encontrada")
    return result


@app.patch("/notes/{title}/rename")
def rename_note_by_title(title: str, request: NoteRenameRequest):
    result = rename_note(title, request.new_title)

    if result is None:
        raise HTTPException(status_code=404, detail="Note not found")
    if "error" in result:
        raise HTTPException(status_code=409, detail=result["error"])

    return result
