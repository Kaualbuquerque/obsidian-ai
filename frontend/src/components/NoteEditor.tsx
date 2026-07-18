import { useEffect, useState } from "react";
import type { NoteDetail, NoteEditorProps } from "../types/notes";
import { Save, Trash2, X } from "lucide-react";
import { maskDate } from "../utils/dateUtils";
import MarkdownEditor from "./MarkdownEditor";

export default function NoteEditor({ selectedNote, onClose, onSaved, onDeleted }: NoteEditorProps) {
    const isNew = selectedNote === '__new__';

    const [title, setTitle] = useState('');
    const [tagInput, setTagInput] = useState('');
    const [compromisso, setCompromisso] = useState('');
    const [date, setDate] = useState('');
    const [content, setContent] = useState('');
    const [originalTitle, setOriginalTitle] = useState('');
    const [tags, setTags] = useState<string[]>([]);
    const [isSaving, setIsSaving] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);

    useEffect(() => {
        if (isNew) {
            const today = new Date();
            const formatted = `${String(today.getDate()).padStart(2, '0')}/${String(today.getMonth() + 1).padStart(2, '0')}/${today.getFullYear()}`;
            setTitle('Nova nota');
            setTags([]);
            setCompromisso('');
            setDate(formatted);
            setContent('');
            return;
        }

        fetch(`http://localhost:8000/notes/${encodeURIComponent(selectedNote)}`)
            .then((r) => r.json())
            .then((data: NoteDetail) => {
                setTitle(data.title);
                setOriginalTitle(data.title)

                const titleLinePattern = new RegExp(`^#\\s*${escapeRegExp(data.title)}\\s*\\n*`);
                const bodyWithoutTitle = data.content.replace(titleLinePattern, '');
                setContent(bodyWithoutTitle);

                const fm = data.frontmatter;
                const rawTags = fm.tags ?? [];
                setTags(Array.isArray(rawTags) ? rawTags : [rawTags]);
                setCompromisso(fm.compromisso ?? '');
                setDate(fm.date ?? '');
            });
    }, [selectedNote]);

    function handleTagKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const newTag = tagInput.trim();
            if (newTag && !tags.includes(newTag)) {
                setTags((prev) => [...prev, newTag]);
            }
            setTagInput('');
        }
    }

    function removeTag(tag: string) {
        setTags((prev) => prev.filter((t) => t !== tag));
    }

    function buildFullContent(): string {
        const tagsYaml = tags.length > 0 ? `[${tags.join(', ')}]` : '[]';
        const frontmatter = `---\ntags: ${tagsYaml}\ncompromisso: ${compromisso}\ndate: ${date}\n---`;

        const titleLinePattern = new RegExp(`^#\\s*${escapeRegExp(title)}\\s*\\n*`);
        const cleanContent = content.replace(titleLinePattern, '');

        return `${frontmatter}\n\n# ${title}\n\n${cleanContent}`;
    }

    function escapeRegExp(text: string): string {
        return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    function handleSave() {
        if (!title.trim()) return;
        setIsSaving(true);

        const fullContent = buildFullContent();

        if (isNew) {
            fetch('http://localhost:8000/notes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, content: fullContent }),
            })
                .then(() => onSaved())
                .finally(() => setIsSaving(false));
            return;
        }

        const saveContent = () =>
            fetch(`http://localhost:8000/notes/${encodeURIComponent(originalTitle)}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: fullContent }),
            });

        const renameIfNeeded = (): Promise<Response | void> => {
            if (title.trim() === originalTitle) return Promise.resolve();
            return fetch(`http://localhost:8000/notes/${encodeURIComponent(originalTitle)}/rename`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ new_title: title.trim() }),
            });
        };

        saveContent()
            .then(() => renameIfNeeded())
            .then(() => onSaved())
            .finally(() => setIsSaving(false));
    }

    function handleDelete() {
        if (isNew) { onClose(); return; }
        setIsDeleting(true);
        fetch(`http://localhost:8000/notes/${encodeURIComponent(selectedNote)}`, {
            method: 'DELETE',
        })
            .then(() => onDeleted())
            .finally(() => setIsDeleting(false));
    }

    const wordCount = content.trim().split(/\s+/).filter(Boolean).length;
    const charCount = content.length;


    return (
        <aside className="h-full bg-surface/30 border-l border-border-hairline flex flex-col">

            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-border-hairline">
                <span className="text-[10px] uppercase tracking-[0.18em] text-foreground/40">
                    Editor de nota
                </span>
                <div className="flex items-center gap-3">
                    <button
                        onClick={handleSave}
                        disabled={isSaving}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border-hairline text-[12px] text-foreground/70 hover:border-accent/40 hover:text-foreground transition-colors disabled:opacity-40"
                    >
                        <Save size={12} />
                        {isSaving ? 'Salvando...' : 'Salvar'}
                    </button>
                    <button
                        onClick={handleDelete}
                        disabled={isDeleting}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border-hairline text-[12px] text-destructive/70 hover:border-destructive/40 hover:text-destructive transition-colors disabled:opacity-40"
                    >
                        <Trash2 size={12} />
                        {isDeleting ? 'Apagando...' : 'Apagar'}
                    </button>
                    <button onClick={onClose} className="text-foreground/40 hover:text-foreground/80 transition-colors">
                        <X size={16} />
                    </button>
                </div>
            </div>

            {/* Title */}
            <div className="px-6 pt-6 pb-3 border-b border-border-hairline">
                <input
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="Título da nota"
                    className="w-full bg-transparent font-serif text-2xl text-foreground placeholder:text-foreground/30 outline-none disabled:opacity-100"
                />
            </div>

            {/* Metadata */}
            <div className="px-6 py-4 border-b border-border-hairline flex flex-col gap-3">

                {/* Tags */}
                <div>
                    <p className="text-[10px] uppercase tracking-[0.12em] text-foreground/40 mb-2">Tags</p>
                    <div className="flex flex-wrap gap-1.5 mb-2">
                        {tags.map((tag) => (
                            <span
                                key={tag}
                                className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-accent-soft border border-accent/20 text-[12px] text-accent"
                            >
                                #{tag}
                                <button onClick={() => removeTag(tag)} className="text-accent/60 hover:text-accent transition-colors">
                                    <X size={10} />
                                </button>
                            </span>
                        ))}
                    </div>
                    <input
                        value={tagInput}
                        onChange={(e) => setTagInput(e.target.value)}
                        onKeyDown={handleTagKeyDown}
                        placeholder="+ Adicionar tag (Enter para confirmar)"
                        className="w-full bg-transparent text-[13px] text-foreground placeholder:text-foreground/30 outline-none"
                    />
                </div>

                {/* Commitment and Date */}
                <div className="grid grid-cols-2 gap-3">
                    <div>
                        <p className="text-[10px] uppercase tracking-[0.12em] text-foreground/40 mb-1">Compromisso</p>
                        <input
                            value={compromisso}
                            onChange={(e) => setCompromisso(e.target.value)}
                            placeholder="Nenhum"
                            className="w-full bg-transparent text-[13px] text-foreground placeholder:text-foreground/30 outline-none"
                        />
                    </div>
                    <div>
                        <p className="text-[10px] uppercase tracking-[0.12em] text-foreground/40 mb-1">Data</p>
                        <input
                            value={date}
                            onChange={(e) => setDate(maskDate(e.target.value))}
                            placeholder="dd/mm/aaaa"
                            maxLength={10}
                            className="w-full bg-transparent text-[13px] text-foreground placeholder:text-foreground/30 outline-none"
                        />
                    </div>
                </div>
            </div>

            {/* Body */}
            <div className="flex-1 py-4 overflow-hidden">
                <MarkdownEditor
                    value={content}
                    onChange={setContent}
                />
            </div>

            {/* Footer */}
            <div className="px-6 py-3 border-t border-border-hairline flex items-center justify-between">
                <span className="text-[11px] text-foreground/30">
                    {wordCount} palavras · {charCount} caracteres
                </span>
                <span className="text-[11px] text-foreground/30 uppercase tracking-wide">
                    Markdown
                </span>
            </div>

        </aside>
    );
}