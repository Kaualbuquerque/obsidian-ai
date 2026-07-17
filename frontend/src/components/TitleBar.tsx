import { useEffect, useState } from 'react';
import { Minus, Square, X } from 'lucide-react';

export default function TitleBar() {
    const [vaultName, setVaultName] = useState('');

    useEffect(() => {
        fetch('http://localhost:8000/vault/name')
            .then((r) => r.json())
            .then((data) => setVaultName(data.name.toUpperCase()));
    }, []);

    return (
        <div
            className="h-10 flex items-center justify-between px-4 border-b border-border-hairline bg-background select-none"
            style={{ WebkitAppRegion: 'drag' } as React.CSSProperties}
        >
            <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-accent" />
            </div>

            <div className="flex items-center gap-2 text-[12px] text-foreground/50">
                <span className="font-serif">Teste</span>
                <span className="text-foreground/30">·</span>
                <span className="tracking-[0.12em] uppercase text-[10px]">{vaultName}</span>
            </div>

            <div
                className="flex items-center gap-1"
                style={{ WebkitAppRegion: 'no-drag' } as React.CSSProperties}
            >
                <button
                    onClick={() => window.electron.minimize()}
                    className="w-8 h-8 flex items-center justify-center text-foreground/40 hover:text-foreground/80 hover:bg-surface-2 rounded transition-colors"
                >
                    <Minus size={12} />
                </button>
                <button
                    onClick={() => window.electron.maximize()}
                    className="w-8 h-8 flex items-center justify-center text-foreground/40 hover:text-foreground/80 hover:bg-surface-2 rounded transition-colors"
                >
                    <Square size={12} />
                </button>
                <button
                    onClick={() => window.electron.close()}
                    className="w-8 h-8 flex items-center justify-center text-foreground/40 hover:text-destructive hover:bg-destructive/10 rounded transition-colors"
                >
                    <X size={12} />
                </button>
            </div>
        </div>
    );
}