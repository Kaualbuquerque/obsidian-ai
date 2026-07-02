export function formatDate(date: Date): string {
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
}

export function toISODate(date: Date): string {
    return date.toISOString().split('T')[0];
}

export function noteTemplate(title: string = 'Nova nota'): string {
    const today = new Date();
    return `---
    tags: []
    compromisso:
    date: ${formatDate(today)}
    ---

    #${title}
    
    `
}