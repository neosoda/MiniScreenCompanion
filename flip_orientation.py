import json
from pathlib import Path
import subprocess
import sys

PROJECT_DIR = Path(__file__).resolve().parent
CONFIG_FILE = PROJECT_DIR / "config.json"
PID_FILE = PROJECT_DIR / ".companion.pid"

if not CONFIG_FILE.exists():
    print("[ERROR] config.json not found!")
    sys.exit(1)

with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

current_rot = data.get("screen", {}).get("rotation", 0)
new_rot = 180 if current_rot == 0 else 0
data["screen"]["rotation"] = new_rot

with open(CONFIG_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"[OK] Screen rotation toggled from {current_rot}deg to {new_rot}deg in config.json.")

# Restart background companion
stop_bat = PROJECT_DIR / "stop.bat"
start_bat = PROJECT_DIR / "start_background.bat"

if PID_FILE.exists():
    try:
        pid = int(PID_FILE.read_text().strip())
        import psutil
        if psutil.pid_exists(pid):
            proc = psutil.Process(pid)
            proc.kill()
            print(f"[OK] Killed existing companion process (PID {pid}).")
        PID_FILE.unlink(missing_ok=True)
    except Exception as e:
        print(f"[WARN] Error killing existing process: {e}")

# Launch detached
pythonw_path = Path(sys.executable).parent / "pythonw.exe"
if not pythonw_path.exists():
    pythonw_path = Path(sys.executable)

p = subprocess.Popen(
    [str(pythonw_path), str(PROJECT_DIR / "run.py")],
    cwd=str(PROJECT_DIR),
    creationflags=0x00000008 | 0x00000200,
)
print(f"[OK] Turing Companion restarted with {new_rot}deg rotation (New PID {p.pid}).")
