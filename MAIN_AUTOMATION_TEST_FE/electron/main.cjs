const { app, BrowserWindow, shell } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const http = require('http');
const fs = require('fs');

const API_HOST = '127.0.0.1';
const API_PORT = 8765;
const API_HEALTH = `http://${API_HOST}:${API_PORT}/api/health`;
const DEV_FE_URL = 'http://localhost:5173';

/** @type {import('child_process').ChildProcess | null} */
let backendProcess = null;

function backendDir() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, 'backend');
  }
  return path.resolve(__dirname, '../../MAIN_AUTOMATION_TEST/pack/dist/checklist-backend');
}

function backendExe() {
  const dir = backendDir();
  const exe = path.join(dir, 'checklist-backend.exe');
  if (fs.existsSync(exe)) return exe;
  return null;
}

function startBackend() {
  const exe = backendExe();
  const env = {
    ...process.env,
    PYTHONUTF8: '1',
    PYTHONIOENCODING: 'utf-8',
  };

  if (exe) {
    const dir = path.dirname(exe);
    env.PLAYWRIGHT_BROWSERS_PATH = path.join(dir, 'ms-playwright');
    backendProcess = spawn(exe, ['api'], {
      cwd: dir,
      env,
      windowsHide: true,
      stdio: 'ignore',
    });
    return;
  }

  // Dev fallback: python -m api
  const automationRoot = path.resolve(__dirname, '../../MAIN_AUTOMATION_TEST');
  backendProcess = spawn('python', ['-m', 'api'], {
    cwd: automationRoot,
    env,
    windowsHide: true,
    stdio: 'ignore',
  });
}

function stopBackend() {
  if (backendProcess && !backendProcess.killed) {
    backendProcess.kill();
  }
  backendProcess = null;
}

function waitForApi(timeoutMs = 45000) {
  const started = Date.now();
  return new Promise((resolve, reject) => {
    const tick = () => {
      const req = http.get(API_HEALTH, (res) => {
        res.resume();
        if (res.statusCode === 200) resolve(true);
        else retry();
      });
      req.on('error', retry);
      req.setTimeout(2000, () => {
        req.destroy();
        retry();
      });
    };
    const retry = () => {
      if (Date.now() - started > timeoutMs) reject(new Error('API timeout'));
      else setTimeout(tick, 500);
    };
    tick();
  });
}

async function createWindow() {
  const win = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 1024,
    minHeight: 640,
    title: 'Checklist Tester — H2Q',
    autoHideMenuBar: true,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  win.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  if (app.isPackaged) {
    await win.loadFile(path.join(__dirname, '../dist/index.html'));
  } else if (process.env.ELECTRON_DEV_URL) {
    await win.loadURL(process.env.ELECTRON_DEV_URL);
  } else {
    await win.loadURL(DEV_FE_URL);
  }
}

app.whenReady().then(async () => {
  startBackend();
  try {
    await waitForApi();
    await createWindow();
  } catch (err) {
    console.error(err);
    app.quit();
  }
});

app.on('window-all-closed', () => {
  stopBackend();
  if (process.platform !== 'darwin') app.quit();
});

app.on('before-quit', () => stopBackend());
