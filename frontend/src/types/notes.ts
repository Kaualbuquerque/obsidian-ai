export interface NotesStats {
    total: number;
    orphans: number;
    tags: Record<string, number>;
}

export interface NotesCalendar {
    dates: Record<string, string>;
    events: Record<string, string>;
}

export interface SideBarProps {
    onNoteSelect: (title: string) => void;
}