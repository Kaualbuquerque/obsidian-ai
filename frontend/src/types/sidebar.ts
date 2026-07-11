import type { Notes, NotesCalendar, NotesStats } from "./notes";

export interface SideBarProps {
    stats: NotesStats | null;
    calendar: NotesCalendar | null;
    notes: Notes[];
    isLoading: boolean;
    onNoteSelect: (title: string) => void;
    onNewNote: () => void;
    onReindex: () => void;
}

export interface SidebarHandle {
    refresh: () => void;

}