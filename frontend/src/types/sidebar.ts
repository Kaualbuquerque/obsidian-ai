export interface SideBarProps {
    onNoteSelect: (title: string) => void;
    onNewNote: () => void;
}

export interface SidebarHandle {
    refresh: () => void;

}