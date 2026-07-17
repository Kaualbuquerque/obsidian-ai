import { useEffect, useRef } from "react";
import type { MarkdownEditorProps } from "../types/editor";
import { EditorView, keymap } from "@codemirror/view";
import { EditorState } from "@codemirror/state";
import { markdown, markdownLanguage } from '@codemirror/lang-markdown'
import { defaultKeymap, history, historyKeymap } from '@codemirror/commands'
import { languages } from '@codemirror/language-data'
import { syntaxHighlighting } from "@codemirror/language";
import { liveMarkDownPlugin } from "../lib/liveMarkdownPlugin";
import { markdownHighlightStyle } from "../lib/markdownHighlight";

export default function MarkdownEditor({ value, onChange }: MarkdownEditorProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const viewRef = useRef<EditorView | null>(null);

    useEffect(() => {
        if (!containerRef.current) return;

        const view = new EditorView({
            state: EditorState.create({
                doc: value,
                extensions: [
                    history(),
                    keymap.of([...defaultKeymap, ...historyKeymap]),
                    markdown({
                        base: markdownLanguage,
                        codeLanguages: languages,
                    }),
                    syntaxHighlighting(markdownHighlightStyle),
                    liveMarkDownPlugin,
                    EditorView.lineWrapping,
                    EditorView.updateListener.of((update) => {
                        if (update.docChanged) {
                            onChange(update.state.doc.toString());
                        }
                    }),
                    EditorView.theme({
                        '&': {
                            height: '100%',
                            fontFamily: 'var(--font-mono)',
                            fontSize: '13px',
                            backgroundColor: 'transparent',
                            color: 'var(--color-foreground)',
                        },
                        '.cm-content': {
                            padding: '0 4px 4rem 4px',
                            caretColor: 'var(--color-accent)',
                        },
                        '.cm-line': {
                            lineHeight: '1.7',
                        },
                        '.cm-focused': {
                            outline: 'none',
                        },
                        '.cm-editor': {
                            height: '100%',
                        },
                        '.cm-scroller': {
                            fontFamily: 'var(--font-mono)',
                            overflow: 'auto',
                        },
                        '&.cm-focused .cm-cursor': {
                            borderLeftColor: 'var(--color-accent)',
                        },
                        '.cm-gutters': {
                            display: 'none',
                        },
                    }),
                ],
            }),
            parent: containerRef.current,
        });

        viewRef.current = view;

        return () => {
            view.destroy();
        };
    }, []);

    useEffect(() => {
        const view = viewRef.current;
        if (!view) return;

        const current = view.state.doc.toString();
        if (current !== value) {
            view.dispatch({
                changes: { from: 0, to: current.length, insert: value },
            });
        }
    }, [value]);

    return (
        <div
            ref={containerRef}
            className="h-full w-full overflow-auto custom-scrollbar"
        />
    )
}