import { useCallback, useState } from "react";
import { type NotesCalendar, type NotesStats, type Notes, type VaultData } from "../types/notes";

export function useVaultData(): VaultData {
    const [stats, setStats] = useState<NotesStats | null>(null);
    const [calendar, setCalendar] = useState<NotesCalendar | null>(null);
    const [notes, setNotes] = useState<Notes[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    const refresh = useCallback(() => {
        setIsLoading(true);

        Promise.all([
            fetch('http://localhost:8000/notes/stats').then((r) => r.json()),
            fetch('http://localhost:8000/notes/calendar').then((r) => r.json()),
            fetch('http://localhost:8000/notes').then((r) => r.json()),
        ])
            .then(([newStats, newCalendar, newNotes]) => {
                setStats(newStats);
                setCalendar(newCalendar);
                setNotes(newNotes);
            })
            .finally(() => setIsLoading(false));
    }, []);

    return { stats, calendar, notes, isLoading, refresh };
}