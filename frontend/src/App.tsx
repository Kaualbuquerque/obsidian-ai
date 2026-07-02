import { useState } from "react";
import Chat from "./components/Chat";
import Sidebar from "./components/Sidebar";
import { useTheme } from "./hooks/useTheme";

export default function Home() {
    const { isDark, toggleTheme } = useTheme();
    const [selectedNote, setSelectedNote] = useState<string | null>(null);

    return (
        <div className="flex h-screen overflow-hidden bg-background">
            <Sidebar onNoteSelect={setSelectedNote} />
            <Chat isDark={isDark} toggleTheme={toggleTheme} onNoteSelect={setSelectedNote} />
            {selectedNote && (
                <div className="w-105 border-l border-border-hairline">
                    {/* NoteEditor vem aqui */}
                    <p className="p-6 text-foreground/40 text-sm">{selectedNote}</p>
                </div>
            )}
        </div>
    )
}