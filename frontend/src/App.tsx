import { useState } from "react";
import Chat from "./components/Chat";
import Sidebar from "./components/Sidebar";
import { useTheme } from "./hooks/useTheme";
import NoteEditor from "./components/NoteEditor";

export default function Home() {
    const { isDark, toggleTheme } = useTheme();
    const [selectedNote, setSelectedNote] = useState<string | null>(null);

    function handleSaved() {
        setSelectedNote(null);
    }

    function handleDeleted() {
        setSelectedNote(null);
    }

    return (
        <div className="flex h-screen overflow-hidden bg-background">
            <Sidebar
                onNoteSelect={setSelectedNote}
                onNewNote={() => setSelectedNote('__new__')}
            />

            <Chat
                isDark={isDark}
                toggleTheme={toggleTheme}
                onNoteSelect={setSelectedNote}
            />

            {selectedNote && (
                <NoteEditor
                    selectedNote={selectedNote}
                    onClose={() => setSelectedNote(null)}
                    onSaved={handleSaved}
                    onDeleted={handleDeleted}
                />
            )}
        </div>
    )
}