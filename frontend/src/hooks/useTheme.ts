import { useEffect, useState } from "react";

export function useTheme() {
    const [isDark, setIsDark] = useState(false);

    useEffect(() => {
        document.documentElement.classList.toggle('dark', isDark);
    }, [isDark]);

    function toggleTheme() {
        setIsDark((prev) => !prev);
    }

    return { isDark, toggleTheme }
}