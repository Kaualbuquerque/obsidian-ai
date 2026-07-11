export async function reindexVault() {
    await fetch('http://localhost:8000/reindex', { method: 'POST' });

    const [resStats, resCalendar, resNotes] = await Promise.all([
        fetch('http://localhost:8000/notes/stats'),
        fetch('http://localhost:8000/notes/calendar'),
        fetch('http://localhost:8000/notes')
    ]);

    const stats = await resStats.json();
    const calendar = await resCalendar.json();
    const notes = await resNotes.json();

    return { stats, calendar, notes };
}