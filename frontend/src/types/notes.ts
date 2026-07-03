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

export interface Note {
    title: string;
    created_at: string;
    tags: string[];
}

export interface NoteDatail {
    title: string;
    content: string;
    frontmatter: Record<string, unknown>;
    tags: string[];
}