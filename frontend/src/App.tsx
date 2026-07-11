import { useEffect, useState } from "react";
import Chat from "./components/Chat";
import Sidebar from "./components/Sidebar";
import { useTheme } from "./hooks/useTheme";
import NoteEditor from "./components/NoteEditor";
import { useVaultData } from "./hooks/useVaultData";

export default function Home() {
    const { isDark, toggleTheme } = useTheme();
    const [selectedNote, setSelectedNote] = useState<string | null>(null);
    const { stats, calendar, notes, isLoading, refresh } = useVaultData();

    useEffect(() => {
        refresh();
    }, []);

    function handleSaved() {
        refresh();
        setSelectedNote(null);
    }

    function handleDeleted() {
        refresh();
        setSelectedNote(null);
    }

    return (
        <div className="flex h-screen overflow-hidden bg-background">
            <Sidebar
                stats={stats}
                calendar={calendar}
                notes={notes}
                isLoading={isLoading}
                onNoteSelect={setSelectedNote}
                onNewNote={() => setSelectedNote('__new__')}
                onReindex={() => {
                    fetch('http://localhost:8000/reindex', { method: 'POST' })
                        .then(() => refresh());
                }}
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