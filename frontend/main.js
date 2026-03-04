/**
 * BlueLock - Electron Main Process
 * Manages: Tray icon, Floating Widget, Popup window, Main vault window
 */

const { app, BrowserWindow, Tray, Menu, ipcMain, nativeImage, screen } = require("electron");
const path = require("path");
const http = require("http");

let tray = null;
let widgetWindow = null;
let popupWindow = null;
let vaultWindow = null;
let recordServer = null;

// ─── App Ready ─────────────────────────────────────────────────────────────────

app.whenReady().then(() => {
  createTray();
  createWidget();
  startRecordServer();
});

app.on("window-all-closed", (e) => {
  e.preventDefault(); // Keep running in tray
});

// ─── Tray Icon ─────────────────────────────────────────────────────────────────

function createTray() {
  // Use a simple colored icon (replace with actual .ico in production)
  const icon = nativeImage.createFromDataURL(getTrayIconBase64());
  tray = new Tray(icon);
  tray.setToolTip("BlueLock — KI Passwort-Manager");

  const contextMenu = Menu.buildFromTemplate([
    {
      label: "🔵 BlueLock öffnen",
      click: () => createOrShowVault(),
    },
    { type: "separator" },
    {
      label: "F3 — Aufnahme starten",
      enabled: false,
    },
    {
      label: "F4 — Autofill",
      enabled: false,
    },
    { type: "separator" },
    {
      label: "Beenden",
      click: () => {
        app.exit(0);
      },
    },
  ]);

  tray.setContextMenu(contextMenu);
  tray.on("double-click", () => createOrShowVault());
}

// ─── Floating Widget ───────────────────────────────────────────────────────────

function createWidget() {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;

  widgetWindow = new BrowserWindow({
    width: 270,
    height: 160,
    x: width - 290,
    y: height - 180,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  widgetWindow.loadFile("widget.html");
  widgetWindow.setIgnoreMouseEvents(false);

  // Make widget draggable but keep position bottom-right
  widgetWindow.on("moved", () => {
    // Optional: snap back to corner
  });
}

// ─── Record Popup ──────────────────────────────────────────────────────────────

function createRecordPopup(screenshotB64) {
  if (popupWindow && !popupWindow.isDestroyed()) {
    popupWindow.focus();
    return;
  }

  const { width, height } = screen.getPrimaryDisplay().workAreaSize;

  popupWindow = new BrowserWindow({
    width: 420,
    height: 480,
    x: Math.round(width / 2 - 210),
    y: Math.round(height / 2 - 240),
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    resizable: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  popupWindow.loadFile("popup.html");

  // Send screenshot to popup once it's ready
  popupWindow.webContents.once("did-finish-load", () => {
    popupWindow.webContents.send("screenshot", screenshotB64);
  });

  popupWindow.on("closed", () => {
    popupWindow = null;
  });
}

// ─── Vault Window ──────────────────────────────────────────────────────────────

function createOrShowVault() {
  if (vaultWindow && !vaultWindow.isDestroyed()) {
    vaultWindow.show();
    vaultWindow.focus();
    return;
  }

  vaultWindow = new BrowserWindow({
    width: 1100,
    height: 700,
    frame: false,
    transparent: true,
    resizable: true,
    minWidth: 800,
    minHeight: 500,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  vaultWindow.loadFile("bluelock.html");

  vaultWindow.on("closed", () => {
    vaultWindow = null;
  });
}

// ─── Record Server (receives F3 trigger from Python) ──────────────────────────

function startRecordServer() {
  recordServer = http.createServer((req, res) => {
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
    res.setHeader("Access-Control-Allow-Headers", "Content-Type");

    if (req.method === "OPTIONS") {
      res.writeHead(200);
      res.end();
      return;
    }

    if (req.method === "POST" && req.url === "/trigger-record") {
      let body = "";
      req.on("data", (chunk) => (body += chunk));
      req.on("end", () => {
        try {
          const { screenshot } = JSON.parse(body);
          createRecordPopup(screenshot);

          // Notify widget
          if (widgetWindow && !widgetWindow.isDestroyed()) {
            widgetWindow.webContents.send("recording-started");
          }

          res.writeHead(200, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ success: true }));
        } catch (e) {
          res.writeHead(400);
          res.end(JSON.stringify({ error: e.message }));
        }
      });
    } else {
      res.writeHead(404);
      res.end();
    }
  });

  recordServer.listen(3131, "127.0.0.1", () => {
    console.log("🔵 BlueLock Electron server on port 3131");
  });
}

// ─── IPC Events (from renderer windows) ───────────────────────────────────────

ipcMain.on("close-popup", () => {
  if (popupWindow && !popupWindow.isDestroyed()) popupWindow.close();
  if (widgetWindow && !widgetWindow.isDestroyed()) {
    widgetWindow.webContents.send("recording-stopped", "saved");
  }
});

ipcMain.on("close-vault", () => {
  if (vaultWindow && !vaultWindow.isDestroyed()) vaultWindow.hide();
});

ipcMain.on("autofill-done", (event, appName) => {
  if (widgetWindow && !widgetWindow.isDestroyed()) {
    widgetWindow.webContents.send("autofill-done", appName);
  }
});

// ─── Tray Icon SVG (embedded) ──────────────────────────────────────────────────

function getTrayIconBase64() {
  // Simple blue lock icon as data URL (16x16)
  return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAbwAAAG8B8aLcQwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAFMSURBVDiNpZMxSgNBFIa/2d0kG9hCCgsLQbSxsPMEHkA8gHgFL+ABPIQewNrGUlAQC0FhFAtBsDGImM3u7DiOZhMkaDDqwMDwmP99//szzIiZKaXEzMxMKaU451JKiTHGiDHm3jlXhxDWZrYELpxzNfBiZi9AI8k5dwO0gZeImQEnwBqQgB9gBCTgFDiW9C5pBnQlHUnaSupLuoqIJfABzIFroF3SrcCBpA1J+5I2JfUi4iwijoEd4A44BD4lxY4R0AEugTbQiYht4AbYBj6AN2AKzIE7YA08AC/AHliqNDMzs97MHoFH4A4YAivgFuj1ANQJ2AAWwA64A87NbFjSzMy6e89sZnsFtIBnYCmpBlyaWQNgZnaZmTHm2TlXA2tmVgALM1sCK2CemVkFbIFdYA9cAwugB+wCO8CjpCdJQ0lXkk6BM+AU6KWU3gHnXA1cA7PsAAAAASUVORK5CYII=";
}
