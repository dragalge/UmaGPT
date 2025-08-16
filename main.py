import time
import pygetwindow as gw
import threading
import uvicorn
import keyboard

from core.execute import career_lobby
import core.state as state
from server.main import app

hotkey = "f1"

def focus_umamusume():
  try:
    win = gw.getWindowsWithTitle("Umamusume")[0]
    if win.isMinimized:
      win.restore()
    else:
      win.minimize()
      time.sleep(0.2)
      win.restore()
      time.sleep(0.5)
  except Exception as e:
    print(f"Error focusing window: {e}")
    return False
  return True

def main():
  print("Uma Auto!")
  if focus_umamusume():
    state.reload_config()
    career_lobby()
  else:
    print("Failed to focus Umamusume window")

def hotkey_listener():
  while True:
    keyboard.wait(hotkey)
    if not state.is_bot_running:
      print("[BOT] Starting...")
      state.is_bot_running = True
      t = threading.Thread(target=main, daemon=True)
      t.start()
    else:
      print("[BOT] Stopping...")
      state.is_bot_running = False
    time.sleep(0.5)

def start_server():
  host = "127.0.0.1"
  port = 8000
  print(f"[INFO] Press '{hotkey}' to start/stop the bot.")
  print(f"[SERVER] Open http://{host}:{port} to configure the bot.")
  config = uvicorn.Config(app, host=host, port=port, workers=1, log_level="warning")
  server = uvicorn.Server(config)
  server.run()

if __name__ == "__main__":
  threading.Thread(target=hotkey_listener, daemon=True).start()
  start_server()
