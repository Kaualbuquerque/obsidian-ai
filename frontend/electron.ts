import { app, BrowserWindow } from 'electron'

function createWindow(): void {
    const win = new BrowserWindow({
        width: 1280,
        height: 800,
        webPreferences: {
            contextIsolation: true
        }
    });

    win.loadURL('http://localhost:5173');
}

app.whenReady().then(createWindow);