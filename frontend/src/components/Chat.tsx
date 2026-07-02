import { useEffect, useRef, useState } from "react";
import type { ChatMessage, ChatProps } from "../types/chat";
import { parseAIResponse } from "../utils/chatUtils";
import { ArrowUp, FileText, Moon, Sun } from "lucide-react";
import UserMessage from "./UserMessage";

function getGreeting(): string {
    const hour = new Date().getHours();
    if (hour < 12) return 'Bom dia.';
    if (hour < 18) return 'Boa tarde.';
    return 'Boa noite.';
}

export default function Chat({ isDark, toggleTheme, onNoteSelect }: ChatProps) {
    const [history, setHistory] = useState<ChatMessage[]>([]);
    const [question, setQuestion] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const bottomRef = useRef<HTMLDivElement>(null);
    const abortControllerRef = useRef<AbortController | null>(null)


    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [history])

    function handleSend() {
        if (!question.trim() || isLoading) return;

        abortControllerRef.current = new AbortController();

        const userMessage: ChatMessage = { role: 'user', content: question };
        setHistory((prev) => [...prev, userMessage]);
        setQuestion('');
        setIsLoading(true);

        fetch('http://localhost:8000/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question.trim() }),
            signal: abortControllerRef.current.signal,
        })
            .then((r) => r.json())
            .then((data) => {
                const { text, sources } = parseAIResponse(data.answer);
                const aiMessage: ChatMessage = {
                    role: 'assistant',
                    content: text,
                    sources,
                };
                setHistory((prev) => [...prev, aiMessage]);
            }).catch((err) => {
                if (err.name !== 'AbortError') {
                    const errorMessage: ChatMessage = {
                        role: 'assistant',
                        content: 'Não foi possível obter uma resposta. Verifique se o servidor está rodando e tente novamente.',
                        sources: [],
                    };
                    setHistory((prev) => [...prev, errorMessage]);
                }
            })
            .finally(() => setIsLoading(false));
    }

    function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    }

    function handleClear() {
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
        }
        setHistory([]);
        setQuestion('');
        setIsLoading(false);
    }

    return (
        <div className="flex-1 flex flex-col h-screen bg-background">

            {/* Header */}
            <div className="flex items-center justify-between px-8 py-4 border-b border-border-hairline">
                <span className="text-[13px] text-foreground/60">Conversa</span>
                <div className="flex items-center gap-4">
                    <button onClick={toggleTheme} className="text-foreground/40 hover:text-foreground/80 transition-colors text-[18px]">
                        {isDark ? <Sun size={18} /> : <Moon size={20} />}
                    </button>
                    <button onClick={handleClear} className="flex items-center gap-1.5 text-[13px] text-foreground/40 hover:text-foreground/80 transition-colors">
                        Limpar
                    </button>
                </div>
            </div>

            {/* Área de mensagens */}
            <div className="flex-1 overflow-y-auto overflow-x-hidden px-8 py-6">
                {history.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-center max-w-lg mx-auto">
                        <div className="w-12 h-12 rounded-[15px] bg-accent/10 flex items-center justify-center mb-6 border border-accent">
                            <span className="w-2.5 h-2.5 rounded-full bg-accent block" />
                        </div>
                        <h2 className="font-serif text-3xl text-foreground mb-2">
                            {getGreeting()} <em>Sobre o que pensamos hoje?</em>
                        </h2>
                        <p className="text-[14px] text-foreground/50 mb-8">
                            Pergunte qualquer coisa sobre suas notas. Toda resposta cita as fontes do seu cofre.
                        </p>
                    </div>
                ) : (
                    <div className="max-w-5xl mx-auto flex flex-col gap-6 font-semibold">
                        {history.map((msg, i) => (
                            <div key={i}>
                                {msg.role === 'user' ? (
                                    <UserMessage content={msg.content} />
                                ) : (
                                    <div className="flex flex-col gap-3 max-w-4xl text-justify">
                                        {msg.content.split('\n').filter(line => line.trim() !== '').map((paragraph, i) => (
                                            <p key={i} className="text-[14px] text-foreground leading-relaxed">
                                                {paragraph}
                                            </p>
                                        ))}
                                        {msg.sources && msg.sources.length > 0 && (
                                            <div className="flex flex-col gap-2">
                                                <span className="text-[10px] uppercase tracking-[0.12em] text-foreground/40">
                                                    Fontes do cofre
                                                </span>
                                                <div className="flex flex-wrap gap-2">
                                                    {msg.sources.map((source) => (
                                                        <button
                                                            key={source}
                                                            onClick={() => onNoteSelect(source)}
                                                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border-hairline text-[12px] text-foreground/60 hover:border-accent/40 hover:text-foreground/80 transition-colors"
                                                        >
                                                            <FileText size={12} className="opacity-50" />
                                                            {source}
                                                        </button>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        ))}
                        {isLoading && (
                            <div className="flex gap-1.5 items-center">
                                <span className="w-1.5 h-1.5 rounded-full bg-foreground/30 animate-bounce [animation-delay:0ms]" />
                                <span className="w-1.5 h-1.5 rounded-full bg-foreground/30 animate-bounce [animation-delay:150ms]" />
                                <span className="w-1.5 h-1.5 rounded-full bg-foreground/30 animate-bounce [animation-delay:300ms]" />
                            </div>
                        )}
                        <div ref={bottomRef} />
                    </div>
                )}
            </div>

            {/* Input */}
            <div className="px-8 py-4 border-t border-border-hairline">
                <div className="max-w-2xl mx-auto">
                    <div className="flex items-center gap-3 bg-surface-2 border border-border-hairline rounded-2xl px-4 py-3 focus-within:border-accent">
                        <textarea
                            value={question}
                            onChange={(e) => {
                                setQuestion(e.target.value);
                                e.target.style.height = 'auto';
                                e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
                            }}
                            onKeyDown={handleKeyDown}
                            placeholder="Pergunte algo sobre suas notas..."
                            rows={1}
                            className="flex-1 bg-transparent text-[14px] text-foreground placeholder:text-foreground/30 outline-none leading-relaxed overflow-y-scroll overflow-x-hidden hide-scrollbar resize-none align-middle selection:border-accent"
                            style={{ height: '24px', maxHeight: '120px' }}
                        />
                        <button
                            onClick={handleSend}
                            disabled={!question.trim() || isLoading}
                            className="w-10 h-8 rounded-xl bg-accent flex items-center justify-center text-accent-foreground cursor-pointer disabled:cursor-auto disabled:opacity-30 transition-opacity shrink-0"
                        >
                            <ArrowUp size={16} />
                        </button>
                    </div>
                    <p className="text-center text-[11px] text-foreground/30 mt-2">
                        Enter envia · Shift+Enter quebra linha
                    </p>
                </div>
            </div>

        </div>
    );
}