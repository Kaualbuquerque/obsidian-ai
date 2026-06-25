import { useEffect, useState } from "react";
import type { NotesCalendar, NotesStats } from "../types/notes";
import { buildCalendarGrid } from "../utils/calendarUtils";

export default function Sidebar() {
    const [stats, setStats] = useState<NotesStats | null>(null);
    const [calendar, setCalendar] = useState<NotesCalendar | null>(null);
    const [currentMonth, setCurrentMonth] = useState(new Date().getMonth() + 1);
    const [currentYear, setCurrentYear] = useState(new Date().getFullYear());

    useEffect(() => {
        fetch('http://localhost:8000/notes/stats')
            .then((response) => response.json())
            .then((data: NotesStats) => setStats(data))

        fetch('http://localhost:8000/notes/calendar')
            .then((response) => response.json())
            .then((data: NotesCalendar) => setCalendar(data))
    }, [])

    if (!stats || !calendar) {
        return <div>Carregando...</div>;
    }

    const datesWithNotes = new Set(Object.values(calendar.dates));
    const eventDates = new Set(Object.keys(calendar.events));
    const grid = buildCalendarGrid(currentYear, currentMonth, datesWithNotes, eventDates)

    return (
        <div>
            <h2>Obsidius</h2>
            <p>Notas: {stats?.total}</p>
            <p>Órfãs: {stats?.orphans}</p>

            <h3>Tags</h3>
            <ul>
                {Object.entries(stats.tags).map(([tag, count]) => (
                    <li key={tag}>#{tag} ({count})</li>
                ))}
            </ul>

            <h3>Calendário — {currentMonth}/{currentYear}</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '4px' }}>
                {grid.map((d, index) => (
                    <div key={index}>
                        {d.isEmpty ? '' : d.day}
                        {d.hasNotes ? '●' : ''}
                        {d.hasEvent ? '🗓' : ''}
                    </div>
                ))}
            </div>
        </div>
    );
}