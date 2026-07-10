import { forwardRef, useEffect, useImperativeHandle, useState } from "react";
import { type Note, type NotesCalendar, type NotesStats } from "../types/notes";
import { buildCalendarGrid, MONTH_NAMES, WEEKDAY_LABELS } from "../utils/calendarUtils";
import { Plus, RefreshCw } from "lucide-react";
import type { SideBarProps, SidebarHandle } from "../types/sidebar";

const Sidebar = forwardRef<SidebarHandle, SideBarProps>(({ onNoteSelect, onNewNote }, ref) => {
    const [stats, setStats] = useState<NotesStats | null>(null);
    const [calendar, setCalendar] = useState<NotesCalendar | null>(null);
    const [selectedDate, setSelectedDate] = useState<string | null>(null);
    const [selectedTag, setSelectedTag] = useState<string | null>(null);
    const [notes, setNotes] = useState<Note[]>([]);
    const [isReindexing, setIsReindexing] = useState(false);
    const [currentMonth, setCurrentMonth] = useState(new Date().getMonth() + 1);
    const [currentYear, setCurrentYear] = useState(new Date().getFullYear());

    function fetchData() {
        fetch('http://localhost:8000/notes/stats')
            .then((r) => r.json())
            .then((data: NotesStats) => setStats(data));

        fetch('http://localhost:8000/notes/calendar')
            .then((r) => r.json())
            .then((data: NotesCalendar) => setCalendar(data));

        fetch('http://localhost:8000/notes')
            .then((r) => r.json())
            .then((data: Note[]) => setNotes(data));
    }

    useImperativeHandle(ref, () => ({
        refresh() {
            fetchData();
        }
    }));

    useEffect(() => {
        fetchData();
    }, []);

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
            setCurrentMonth((prev) => prev + 1);
        }
    }

    function handleDayClick(day: number) {
        const monthStr = String(currentMonth).padStart(2, '0');
        const dayStr = String(day).padStart(2, '0');
        const dateKey = `${currentYear}-${monthStr}-${dayStr}`;
        setSelectedDate((prev) => (prev === dateKey ? null : dateKey));
    }

    function handleReindex() {
        setIsReindexing(true);
        fetch('http://localhost:8000/reindex', { method: 'POST' })
            .then(() => Promise.all([
                fetch('http://localhost:8000/notes/stats').then((r) => r.json()),
                fetch('http://localhost:8000/notes/calendar').then((r) => r.json()),
                fetch('http://localhost:8000/notes').then((r) => r.json()),
            ]))
            .then(([newStats, newCalendar, newNotes]) => {
                setStats(newStats);
                setCalendar(newCalendar);
                setNotes(newNotes);
            })
            .finally(() => setIsReindexing(false));
    }

    const datesWithNotes = calendar ? new Set(Object.values(calendar.dates)) : new Set<string>();
    const eventDates = calendar ? new Set(Object.keys(calendar.events)) : new Set<string>();
    const grid = buildCalendarGrid(currentYear, currentMonth, datesWithNotes, eventDates, selectedDate);

    if (!stats || !calendar) {
        return (
            <aside className="w-90 h-screen bg-surface/40 border-r border-border-hairline flex items-center justify-center">
                <p className="text-[13px] text-foreground/40">Carregando...</p>
            </aside>
        );
    }

    return (
        <aside className="w-90 h-screen bg-surface/40 border-r border-border-hairline flex flex-col p-6">
            <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-accent" />
                    <h1 className="font-serif text-2xl text-foreground">Obsidius</h1>
                </div>
                <button
                    onClick={onNewNote}
                    className="text-foreground/40 border border-accent/40 hover:text-foreground/80 hover:border-accent rounded-md transition-colors"
                >
                    <Plus size={20} />
                </button>
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
                                    `}
                                >
                                    {d.day}
                                    {(d.hasNotes || d.hasEvent) && !d.isSelected && (
                                        <span className={`absolute bottom-0.5 w-1 h-1 rounded-full ${d.hasEvent ? 'bg-accent' : 'bg-foreground/30'}`} />
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
                            key={tag}
                            onClick={() => setSelectedTag((prev) => (prev === tag ? null : tag))}
                            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-[13px] transition-colors
                                ${selectedTag === tag
                                    ? 'border-accent text-accent bg-accent-soft'
                                    : 'border-border-hairline text-foreground/80 hover:border-accent/40'
                                }`}
                        >
                            #{tag}
                            <span className="text-foreground/40">{count}</span>
                        </button>
                    ))}
                </div>
            </div>

            {(selectedDate || selectedTag) && (
                <div className="mt-6">
                    <p className="text-[10px] uppercase tracking-[0.12em] text-foreground/50 mb-3">
                        {selectedTag ? `Notas com #${selectedTag}` : `Notas de ${selectedDate}`}
                    </p>
                    <div className="flex flex-col gap-2">
                        {notes.filter((note) => {
                            if (selectedTag) return note.tags.includes(selectedTag);
                            if (selectedDate) return note.created_at === selectedDate;
                            return false;
                        }).map((note) => (
                            <button
                                key={note.title}
                                onClick={() => onNoteSelect(note.title)}
                                className="w-full text-left px-3 py-2.5 rounded-xl border border-border-hairline hover:border-accent/40 transition-colors"
                            >
                                <p className="text-[13px] text-foreground/80 truncate">{note.title}</p>
                                <p className="text-[11px] text-foreground/40 mt-0.5">{note.created_at}</p>
                            </button>
                        ))}
                        {notes.filter((note) => {
                            if (selectedDate) return note.created_at === selectedDate;
                            return false;
                        }).length === 0 && selectedDate && !selectedTag && (
                                <p className="text-[12px] text-foreground/40">
                                    Nenhuma nota criada nesse dia.
                                </p>
                            )}
                    </div>
                </div>
            )}

            <div className="mt-auto pt-6">
                <button
                    onClick={handleReindex}
                    disabled={isReindexing}
                    className="w-full flex items-center justify-center gap-2 py-3 rounded-xl border border-border-hairline text-[13px] text-foreground/80 hover:border-accent/40 hover:text-foreground transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                >
                    <span className={`transition-transform duration-700 ${isReindexing ? 'animate-spin' : ''}`}>
                        <RefreshCw size={16} />
                    </span>
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
});

export default Sidebar;