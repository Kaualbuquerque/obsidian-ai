export interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
    sources?: string[];
}

export interface ParsedResponse {
    text: string;
    sources: string[];
}

export interface ChatProps {
    isDark: boolean;
    toggleTheme: () => void;
    onNoteSelect: (title: string) => void;
}

export interface UserMessageProps {
    content: string;
}
