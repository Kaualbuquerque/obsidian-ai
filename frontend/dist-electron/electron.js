import { app, BrowserWindow, ipcMain } from 'electron';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const isDev = !app.isPackaged;
function createWindow() {
    const preloadPath = join(__dirname, 'preload.js');
    console.log('Preload path:', preloadPath);
    const win = new BrowserWindow({
        width: 1280,
        height: 800,
        frame: false,
        backgroundColor: '#1F1E1C',
        icon: join(__dirname, '../build/icon.png'),
        webPreferences: {
            contextIsolation: true,
            preload: join(__dirname, 'preload.js'),
        },
    });
    if (isDev) {
        loadWithRetry(win, 'http://localhost:5173');
    }
    else {
        win.loadFile('dist/index.html');
    }
    ipcMain.on('window:minimize', () => win.minimize());
    ipcMain.on('window:maximize', () => {
        if (win.isMaximized()) {
            win.unmaximize();
        }
        else {
            win.maximize();
        }
    });
    ipcMain.on('window:close', () => win.close());
}
function loadWithRetry(win, url, attempt = 1) {
    win.loadURL(url).catch(() => {
        if (attempt < 20) {
            setTimeout(() => loadWithRetry(win, url, attempt + 1), 300);
        }
    });
}
app.whenReady().then(createWindow);
