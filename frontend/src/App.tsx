import Sidebar from "./components/Sidebar";
import { useTheme } from "./hooks/useTheme";

export default function Home() {
    const { isDark, toggleTheme } = useTheme()
    return (
        <div className="flex gap-10">
            <Sidebar />
            <button onClick={toggleTheme} className="bg-accent text-accent-foreground px-4 py-2 rounded-xl">
                Tema atual: {isDark ? 'Escuro' : 'Claro'}
            </button>
        </div>
    )
}