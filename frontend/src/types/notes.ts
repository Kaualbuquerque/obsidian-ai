export interface NotesStats {
    total: number;
    orphans: number;
    tags: Record<string, number>;
}

export interface NotesCalendar {
    dates: Record<string, string>;
    events: Record<string, string>;
}

export interface Note {
    title: string;
    created_at: string;
    tags: string[];
}

export interface NoteFrontmatter {
    tags?: string[];
    compromisso?: string;
    date?: string;
}

export interface NoteDetail {
    title: string;
    content: string;
    frontmatter: NoteFrontmatter;
    tags: string[];
}

export interface NoteEditorProps {
    selectedNote: string;
    onClose: () => void;
    onSaved: () => void;
    onDeleted: () => void;
}