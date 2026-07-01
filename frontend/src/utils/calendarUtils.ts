export interface CalendarDay {
    day: number;
    hasNotes: boolean;
    hasEvent: boolean;
    isEmpty: boolean;
    isToday: boolean;
    isSelected: boolean;
}

export const MONTH_NAMES = [
    'JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN',
    'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ'
];

export const WEEKDAY_LABELS = ['S', 'T', 'Q', 'Q', 'S', 'S', 'D'];

export function getDaysInMonth(year: number, month: number): number {
    return new Date(year, month, 0).getDate()
}

export function getFirstWeekDay(year: number, month: number): number {
    const day = new Date(year, month - 1, 1).getDay();
    return day === 0 ? 6 : day - 1
}

export function buildCalendarGrid(
    year: number,
    month: number,
    datesWithNotes: Set<string>,
    eventDates: Set<string>,
    selectedDate: string | null = null
): CalendarDay[] {
    const totalDays = getDaysInMonth(year, month);
    const fistWeekDay = getFirstWeekDay(year, month);
    const grid: CalendarDay[] = []

    const today = new Date();
    const todayKey = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`

    for (let i = 0; i < fistWeekDay; i++) {
        grid.push({ day: 0, hasNotes: false, hasEvent: false, isEmpty: true, isToday: false, isSelected: false })
    }

    for (let day = 1; day <= totalDays; day++) {
        const monthStr = String(month).padStart(2, '0');
        const dayStr = String(day).padStart(2, '0');
        const dateKey = `${year}-${monthStr}-${dayStr}`;

        grid.push({
            day,
            hasNotes: datesWithNotes.has(dateKey),
            hasEvent: eventDates.has(dateKey),
            isEmpty: false,
            isToday: dateKey === todayKey,
            isSelected: dateKey === selectedDate,
        });
    }

    return grid;
}