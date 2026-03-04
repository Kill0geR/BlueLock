"""
BlueLock - Backend Server
FastAPI server that handles all logic: vault, screenshots, AI matching, autofill
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import threading
import keyboard
import pyautogui
import cv2
import numpy as np
from PIL import ImageGrab
import base64
import io
import time
from vault import Vault
from matcher import ScreenMatcher
from notifier import Notifier

app = FastAPI(title="BlueLock API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

vault = Vault()
matcher = ScreenMatcher()
notifier = Notifier()

# ─── Models ────────────────────────────────────────────────────────────────────

class SaveCredentialRequest(BaseModel):
    app_name: str
    username: str
    password: str
    screenshot_b64: str  # base64 encoded screenshot

class GetAllResponse(BaseModel):
    entries: list

# ─── Routes ────────────────────────────────────────────────────────────────────

@app.get("/ping")
def ping():
    return {"status": "ok", "message": "BlueLock läuft"}


@app.get("/entries")
def get_entries():
    """Get all saved credentials (passwords masked)"""
    entries = vault.get_all()
    # Mask passwords before sending to frontend
    for e in entries:
        e["password"] = "••••••••"
    return {"entries": entries}


@app.post("/save")
def save_credential(req: SaveCredentialRequest):
    """Save new credential with screenshot"""
    try:
        vault.save(
            app_name=req.app_name,
            username=req.username,
            password=req.password,
            screenshot_b64=req.screenshot_b64
        )
        notifier.show("BlueLock", "✓ Ja, gespeichert!")
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/autofill")
def autofill():
    """Take screenshot, find matching entry, autofill credentials"""
    try:
        # Take current screenshot
        screenshot = take_screenshot()
        
        # Find matching entry in vault
        match = matcher.find_match(screenshot, vault.get_all_with_screenshots())
        
        if not match:
            notifier.show("BlueLock", "⚠ Keine passende App gefunden")
            return {"success": False, "message": "Keine passende App gefunden"}
        
        # Autofill the credentials
        do_autofill(match["username"], match["password"])
        
        notifier.show("BlueLock", "✓ Daten wurden erfolgreich hinzugefügt!")
        return {"success": True, "app_name": match["app_name"]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/screenshot")
def get_screenshot():
    """Take and return current screenshot as base64"""
    screenshot_b64 = take_screenshot_b64()
    return {"screenshot": screenshot_b64}


@app.delete("/entries/{entry_id}")
def delete_entry(entry_id: int):
    """Delete a saved entry"""
    vault.delete(entry_id)
    return {"success": True}


@app.get("/stats")
def get_stats():
    """Get vault statistics"""
    return vault.get_stats()

# ─── Helpers ───────────────────────────────────────────────────────────────────

def take_screenshot():
    """Take screenshot and return as numpy array"""
    img = ImageGrab.grab()
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def take_screenshot_b64():
    """Take screenshot and return as base64 string"""
    img = ImageGrab.grab()
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def do_autofill(username: str, password: str):
    """Type username and password into active window"""
    time.sleep(0.3)
    keyboard.write(username, delay=0.05)
    keyboard.press("tab")
    time.sleep(0.1)
    keyboard.write(password, delay=0.05)


# ─── Hotkey Listener ───────────────────────────────────────────────────────────

def start_hotkey_listener():
    """Listen for F3 and F4 globally"""
    import requests

    def on_f3():
        """F3: Signal Electron to open the record popup"""
        try:
            print("f3 wurde gedrückt")
            screenshot_b64 = take_screenshot_b64()
            requests.post("http://localhost:3131/trigger-record", 
                         json={"screenshot": screenshot_b64}, timeout=2)
        except Exception:
            pass

    def on_f4():
        """F4: Trigger autofill — notify Electron widget before and after"""
        try:
            # Tell widget: scanning started
            requests.post("http://localhost:3131/trigger-autofill-start", timeout=2)
        except Exception:
            pass
        try:
            res = requests.post("http://localhost:8000/autofill", timeout=5)
            data = res.json()
            # Tell widget: done (success or not)
            requests.post("http://localhost:3131/trigger-autofill-done",
                          json={"success": data.get("success", False),
                                "app_name": data.get("app_name", "")}, timeout=2)
        except Exception:
            pass

    keyboard.add_hotkey("f3", on_f3)
    keyboard.add_hotkey("f4", on_f4)
    keyboard.wait()


# ─── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Start hotkey listener in background thread
    hotkey_thread = threading.Thread(target=start_hotkey_listener, daemon=True)
    hotkey_thread.start()

    print("🔵 BlueLock Backend läuft auf http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
