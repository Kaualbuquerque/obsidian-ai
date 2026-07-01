import { useEffect, useState } from "react";
import type { NotesCalendar, NotesStats } from "../types/notes";
import { buildCalendarGrid, MONTH_NAMES, WEEKDAY_LABELS } from "../utils/calendarUtils";

export default function Sidebar() {
    const [stats, setStats] = useState<NotesStats | null>(null);
    const [calendar, setCalendar] = useState<NotesCalendar | null>(null);
    const [selectedDate, setSelectedDate] = useState<string | null>(null);
    const [isReindexing, setIsReindexing] = useState(false);
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

    function getDayTextColor(d: { isSelected: boolean; isToday: boolean; hasNotes: boolean; hasEvent: boolean }) {
        if (d.isSelected) return 'text-accent-foreground font-semibold';
        if (d.hasNotes || d.hasEvent) return 'text-foreground';
        return 'text-foreground/40';
    }

    function goToPreviousMonth() {
        if (currentMonth === 1) {
            setCurrentMonth(12);
            setCurrentYear((prev) => prev - 1);
        } else {
            setCurrentMonth((prev) => prev - 1);
        }
    }

    function goToNextMonth() {
        if (currentMonth === 12) {
            setCurrentMonth(1);
            setCurrentYear((prev) => prev + 1);
        } else {
            setCurrentMonth((prev) => prev + 1)
        }
    }

    function handleDayClick(day: number) {
        const monthStr = String(currentMonth).padStart(2, '0');
        const dayStr = String(day).padStart(2, '0');
        const dateKey = `${currentYear}-${monthStr}-${dayStr}`;

        setSelectedDate((prev) => (prev === dateKey ? null : dateKey));
    }

    function handleReindex() {
        setIsReindexing(true)
        fetch('http://localhost:8000/reindex', { method: 'POST' })
            .then(() => {
                return Promise.all([
                    fetch('http://localhost:8000/notes/stats').then((r) => r.json()),
                    fetch('http://localhost:8000/notes/calendar').then((r) => r.json()),
                    console.log("Requisitando as informações")
                ]);
            })
            .then(([newStats, newCalendar]) => {
                setStats(newStats);
                setCalendar(newCalendar);
                console.log(newStats, newCalendar)
            })
            .finally(() => {
                setIsReindexing(false)
            })
    }

    const datesWithNotes = new Set<string>();
    const eventDates = new Set<string>();
    const grid = buildCalendarGrid(currentYear, currentMonth, datesWithNotes, eventDates, selectedDate)

    if (!stats || !calendar) {
        return (
            <aside className="w-90 h-screen bg-surface/40 border-r border-border-hairline flex items-center justify-center">
                <p className="text-[13px] text-foreground/40">Carregando...</p>
            </aside>
        )
    }

    return (
        <aside className="w-90 h-screen bg-surface/40 border-r border-border-hairline flex flex-col p-6">
            <div className="flex items-center gap-2 mb-1">
                <span className="w-2 h-2 rounded-full bg-accent" />
                <h1 className="font-serif text-2xl text-foreground">Obsidius</h1>
            </div>
            <p className="text-[10px] uppercase tracking-[0.18em] text-foreground/50 mb-6">
                Inteligência para o seu cofre
            </p>

            <div className="grid grid-cols-2 gap-3">
                <div className="bg-surface-2 border border-border-hairline rounded-xl p-4 text-center">
                    <p className="font-serif italic text-2xl text-foreground">{stats.total}</p>
                    <p className="text-[10px] uppercase tracking-[0.12em] text-foreground/50 mt-1">
                        Notas Totais
                    </p>
                </div>
                <div className="bg-surface-2 border border-border-hairline rounded-xl p-4 text-center">
                    <p className="font-serif italic text-2xl text-foreground">{stats.orphans}</p>
                    <p className="text-[10px] uppercase tracking-[0.12em] text-foreground/50 mt-1">
                        Órfãs
                    </p>
                </div>
            </div>

            <div className="mt-6">
                <div className="flex items-center justify-between mb-3">
                    <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-foreground/50">
                        {MONTH_NAMES[currentMonth - 1]} {currentYear}
                    </p>
                    <div className="flex gap-1">
                        <button onClick={goToPreviousMonth} className="text-foreground/40 hover:text-foreground/80 px-1">‹</button>
                        <button onClick={goToNextMonth} className="text-foreground/40 hover:text-foreground/80 px-1">›</button>
                    </div>
                </div>

                <div className="grid grid-cols-7 gap-y-2 text-center">
                    {WEEKDAY_LABELS.map((label, i) => (
                        <span key={i} className="text-[10px] text-foreground/40">{label}</span>
                    ))}

                    {grid.map((d, i) => (
                        <div key={i} className="flex items-center justify-center h-8">
                            {!d.isEmpty && (
                                <button
                                    onClick={() => handleDayClick(d.day)}
                                    className={`
                                    relative w-10 h-7 flex items-center justify-center text-[13px] rounded-md
                                    ${getDayTextColor(d)}
                                    ${d.isToday ? 'ring-1 ring-accent' : ''}
                                    ${d.isSelected ? 'bg-accent' : ''}
                                `}>
                                    {d.day}
                                    {(d.hasNotes || d.hasEvent) && !d.isSelected && (
                                        <span
                                            className={`absolute bottom-0.5 w-1 h-1 rounded-full ${d.hasEvent ? 'bg-accent' : 'bg-foreground/30'
                                                }`}
                                        />
                                    )}
                                </button>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            <div className="mt-6">
                <p className="text-[10px] uppercase tracking-[0.12em] text-foreground/50 mb-3">
                    Explorar tags
                </p>
                <div className="flex flex-wrap gap-2">
                    {Object.entries(stats.tags).map(([tag, count]) => (
                        <button
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-border-hairline text-[13px] text-foreground/80 hover:border-accent/40 transition-colors">
                            #{tag}
                            <span className="text-foreground/40">{count}</span>
                        </button>
                    ))}
                </div>
            </div>

            <div className="mt-auto pt-6">
                <button
                    onClick={handleReindex}
                    disabled={isReindexing}
                    className="w-full flex items-center justify-center gap-2 py-3 rounded-xl border border-border-hairline text-[13px] text-foreground/80 hover:border-accent/40 hover:text-foreground transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                >
                    <span className={`text-[15px] transition-transform duration-700 ${isReindexing ? 'animate-spin' : ''}`}>↻</span>
                    <span className="relative">
                        {isReindexing ? 'Reindexando' : 'Reindexar Cofre'}
                        {isReindexing && (
                            <span className="inline-flex w-4 justify-start">
                                <span className="animate-pulse">.</span>
                                <span className="animate-pulse [animation-delay:0.2s]">.</span>
                                <span className="animate-pulse [animation-delay:0.4s]">.</span>
                            </span>
                        )}
                    </span>
                </button>
                <p className="text-center text-[11px] text-foreground/30 mt-3">
                    Vault local · offline-first
                </p>
            </div>
        </aside>
    );
}