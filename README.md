# 🚀 Turing 3.5" Cockpit Companion

Dashboard de télémétrie PC en temps réel pour écran **Turing Smart Screen 3.5" IPS** (USB Type-C, révision Rev A / CH552T `USB35INCHIPSV2`).

![Preview](preview.png)

---

## ⚡ Améliorations & Stabilité (Inspiré de mathoudebine/turing-smart-screen-python)

- **Zero Flicker GPU (NVML Natif)** :
  - Interrogation directe de `nvml.dll` en C-types (< 0.1 ms).
  - Suppression totale des appels CLI `nvidia-smi` en sous-processus.
  - **Fini les clignotements d'écrans PC / G-Sync !**
- **Indépendance Totale (Arrière-plan persistant)** :
  - Lancement via `start_background.bat` en processus détaché (`pythonw.exe`).
  - Fermer Antigravity, VS Code ou les invites de commande n'interrompt pas l'affichage.
  - Verrouillage par Mutex Windows : une seule instance active sur le port COM.
- **Cadence & Fiabilité** :
  - Cycle synchronisé (1.0 s par défaut, réglable dans `config.json`).
  - Reconnexion automatique si l'écran est débranché / rebranché.
  - Écran de veille élégant ("STANDBY") lors de l'arrêt propre.
  - Impact CPU hôte quasiment nul (< 0.2%).

---

## 🛠️ Utilisation

### 1. Démarrer en arrière-plan (Recommandé)
Double-cliquez sur :
👉 [start_background.bat](file:///A:/PROJETS/Mini%20Screen%20Companion/start_background.bat)
*(Fonctionne de manière totalement autonome et invisible)*

### 2. Vérifier l'état
Double-cliquez sur :
👉 [status.bat](file:///A:/PROJETS/Mini%20Screen%20Companion/status.bat)
*(Affiche le PID, la mémoire consommée et les 10 dernières lignes du journal)*

### 3. Arrêter proprement
Double-cliquez sur :
👉 [stop.bat](file:///A:/PROJETS/Mini%20Screen%20Companion/stop.bat)
*(Affiche l'écran Standby sur le Turing 3.5 et libère le port COM)*

### 4. Démarrage automatique avec Windows
- **Activer** : Double-cliquez sur [install_startup.bat](file:///A:/PROJETS/Mini%20Screen%20Companion/install_startup.bat).
- **Désactiver** : Double-cliquez sur [uninstall_startup.bat](file:///A:/PROJETS/Mini%20Screen%20Companion/uninstall_startup.bat).

---

## ⚙️ Configuration (`config.json`)

```json
{
  "screen": {
    "port": "AUTO",
    "baudrate": 115200,
    "width": 480,
    "height": 320,
    "orientation": "landscape",
    "rotation": 0,
    "brightness": 80
  },
  "telemetry": {
    "interval_sec": 1.0,
    "history_length": 30,
    "mode": "sync"
  }
}
```
