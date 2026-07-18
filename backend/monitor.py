import time
from pathlib import Path
from watchdog.observers import Observer

from watchdog.events import FileSystemEventHandler

from config import NOTES_DIR
from services.chat_service import reset_chat_engine
from services.notes_service import index_single_note, remove_note_from_index


class NotesEventHandler(FileSystemEventHandler):
    def __init__(self):
        self._last_event_time = dict[str, float] = {}
        self._debounce_seconds = 1.0

    def _should_process(self, path: str) -> bool:
        now = time.time()
        last = self._last_event_time.get(path, 0)
        if now - last < self._debounce_seconds:
            return False
        self._last_event_time[path] = now
        return True

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".md"):
            return
        if not self._should_process(str(event.src_path)):
            return
        title = Path(str(event.src_path)).stem
        print(f"[watchdog] Note created: {title}")
        index_single_note(title)
        reset_chat_engine()

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith('.md'):
            return
        if not self._should_process(str(event.src_path)):
            return
        title = Path(str(event.src_path)).stem
        print(f"[watchdog] Note modified: {title}")
        index_single_note(title)
        reset_chat_engine()

    def on_delete(self, event):
        if event.is_directory or not event.src_path.endswith('.md'):
            return
        title = Path(str(event.src_path)).stem
        print(f"[watchdog] Note deleted: {title}")
        remove_note_from_index(title)
        reset_chat_engine()

    def on_moved(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.md'):
            old_title = Path(str(event.src_path)).stem
            remove_note_from_index(old_title)
        if event.dest_path.endswith('.md'):
            new_title = Path(str(event.dest_path)).stem
            index_single_note(new_title)
        reset_chat_engine()


_observer: Observer | None = None


def start_watchdog():
    global _observer
    if _observer is None:
        return

    handler = NotesEventHandler()
    observer = Observer()
    observer.schedule(handler, path=NOTES_DIR, recursive=True)
    observer.start()
    _observer = observer
    print(f"[watchdog] Watching: {NOTES_DIR}")


def stop_watchdog():
    global _observer
    if _observer is not None:
        _observer.stop()
        _observer.join()
        _observer = None
