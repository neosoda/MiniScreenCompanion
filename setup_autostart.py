from __future__ import annotations

import os
import sys
from pathlib import Path
import win32com.client


def install():
    appdata = os.environ.get("APPDATA")
    if not appdata:
        print("[ERREUR] Variable APPDATA introuvable.")
        return

    startup_dir = Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    startup_dir.mkdir(parents=True, exist_ok=True)
    shortcut_path = startup_dir / "Turing-3.5-Companion.lnk"

    project_dir = Path(__file__).resolve().parent
    run_script = project_dir / "run.py"

    pythonw_exe = Path(sys.executable).parent / "pythonw.exe"
    if not pythonw_exe.exists():
        pythonw_exe = Path(sys.executable)

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(str(shortcut_path))
    shortcut.TargetPath = str(pythonw_exe)
    shortcut.Arguments = f'"{run_script}"'
    shortcut.WorkingDirectory = str(project_dir)
    shortcut.Description = "Turing 3.5 Cockpit Companion Autostart"
    shortcut.WindowStyle = 7  # Minimized / Silent
    shortcut.Save()

    print(f"[OK] Raccourci de demarrage installe avec succes !")
    print(f"     Fichier : {shortcut_path}")
    print(f"     Cible   : {pythonw_exe} \"{run_script}\"")
    print(f"     Dossier : {project_dir}")


def uninstall():
    appdata = os.environ.get("APPDATA")
    if not appdata:
        return
    shortcut_path = Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup" / "Turing-3.5-Companion.lnk"
    if shortcut_path.exists():
        shortcut_path.unlink()
        print(f"[OK] Raccourci supprime de Startup : {shortcut_path}")
    else:
        print("[INFO] Aucun raccourci trouve dans Startup.")


if __name__ == "__main__":
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "install"
    if mode == "uninstall":
        uninstall()
    else:
        install()
