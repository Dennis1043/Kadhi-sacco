const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let flaskProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  // Load the Flask app URL
  mainWindow.loadURL('http://127.0.0.1:5000/index.html');

  mainWindow.on('closed', () => {
    mainWindow = null;
    if (flaskProcess) {
      flaskProcess.kill();
    }
  });
}

app.whenReady().then(() => {
  // Start Flask backend executable
  const exePath = path.join(__dirname, 'dist', 'app.exe'); // path to compiled Flask app
  flaskProcess = spawn(exePath, [], { shell: true });

  flaskProcess.stdout.on('data', (data) => {
    console.log(`Flask: ${data}`);
  });

  flaskProcess.stderr.on('data', (data) => {
    console.error(`Flask Error: ${data}`);
  });

  flaskProcess.on('close', (code) => {
    console.log(`Flask process exited with code ${code}`);
  });

  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    if (flaskProcess) flaskProcess.kill();
    app.quit();
  }
});
