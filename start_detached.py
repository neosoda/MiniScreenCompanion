#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

PROJECT_DIR = Path(__file__).resolve().parent
RUN_SCRIPT = PROJECT_DIR / "run.py"

python_dir = Path(sys.executable).parent
pythonw_candidates = [
    python_dir / "pythonw.exe",
    Path(r"C:\Users\NEO.NEO-PC\AppData\Local\Programs\Python\Python312\pythonw.exe"),
]

pythonw_exe = None
for cand in pythonw_candidates:
    if cand.exists():
        pythonw_exe = str(cand)
        break

if not pythonw_exe:
    pythonw_exe = sys.executable

# Standard detached flags for pythonw on Windows
DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

flags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP

proc = subprocess.Popen(
    [pythonw_exe, str(RUN_SCRIPT)] + sys.argv[1:],
    cwd=str(PROJECT_DIR),
    creationflags=flags,
    stdin=subprocess.DEVNULL,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    close_fds=True,
)

print(f"[OK] Turing 3.5 Companion demarre en arriere-plan (PID: {proc.pid})")
print("     Le processus est detache : tu peux fermer Antigravity et les fenetres sans interrompre l'ecran.")
