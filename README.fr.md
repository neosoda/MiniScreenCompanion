<div align="center">

# 🎮 Mini Screen Companion

### Tamagotchi de Dev Pixel Art Autonome & Moniteur de Quotas IA en Direct

**Suivi en direct des quotas Claude Code, OpenAI Codex & Google Gemini pour horloges connectées GeekMagic, SmallTV et écrans de bureau ESP8266/ESP32.**

<br/>

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-F59E0B.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Architecture: Clean](https://img.shields.io/badge/architecture-immuable%20%26%20idempotent-10B981.svg?style=for-the-badge)]()
[![Platform](https://img.shields.io/badge/plateforme-Windows%20%7C%20macOS%20%7C%20Linux-6366F1.svg?style=for-the-badge)]()

<br/>

<img src="assets/preview.gif" alt="Mini Screen Companion Aperçu Animé" width="340"/>

<p align="center">
  <b>Ne soyez plus jamais bloqué par les limites de requêtes IA au milieu d'un hack intensif.</b><br/>
  1/3 chambre pixel art avec avatar vivant &bull; 2/3 HUD haute lisibilité avec double jauge par fournisseur.
</p>

[🇬🇧 English](README.md) • [✨ Fonctionnalités](#-fonctionnalités) • [🚀 Démarrage Rapide](#-démarrage-rapide) • [⚙️ Configuration](#️-configuration) • [🛠️ Commandes CLI](#️-commandes-en-ligne-de-commande-cli) • [🏗️ Architecture](#️-architecture)

</div>

---

## ✨ Fonctionnalités

- **🎮 1/3 Tamagotchi de Dev Vivant (Tiers Haut 80px)** :
  - **Machine à États Autonome** : Réagit en direct à votre activité de code, à l'heure du jour et aux cycles de pause.
  - **Postures Dynamiques** :
    - 💻 **En Plein Hack** : Tape frénétiquement au clavier d'un PC portable lumineux avec code coloré et tasse de café fumante.
    - ☕ **Pause Café** : Debout près de la fenêtre ensoleillée buvant son café avec vapeur animée.
    - 🐱 **Câlin Chat** : Assis par terre caressant un chat roux qui ronronne et remue la queue.
    - 🏃 **Jogging Matin / Soir** : Petite course dynamique à travers la pièce.
    - 🌙 **Dodo Nuit** : Endormi au chaud sous une couverture bleue avec « *z Z z* » flottants.
  - **Éclairage Ambiant Jour & Nuit** : Ciel bleu ensoleillé avec rayons de lumière vs nuit étoilée avec croissant de lune.
  - **Style Chibi Anime Mignon** : Peau claire, joues roses, grands yeux manga expressifs et cheveux bruns.
  - **Support d'Avatar Personnalisé** : Déposez votre propre GIF ou sprite animé dans `assets/avatar/custom.gif` pour l'animer automatiquement !

- **📊 2/3 HUD Quotas Haute Lisibilité (Deux Tiers Bas 160px)** :
  - **Claude Code** (Anthropic) &bull; **OpenAI Codex** &bull; **Google Gemini** affichés simultanément.
  - **Double Jauge par Fournisseur** :
    - **Session 5H** : Pourcentage disponible + compte à rebours précis jusqu'au reset (ex: `2h40m`).
    - **Plafond 7J** : Quota hebdomadaire restant en jours/heures (ex: `5j02h`).
  - **Icônes Rétro 8-bit** : Invader corail (Claude), nuage terminal violet (Codex) et étoile brillante cyan (Gemini).
  - **Couleurs Dynamiques** : Vert émeraude (>25%), ambre d'avertissement (10–25%) et rouge d'alerte (<10%).

- **⚡ Zéro Configuration Requise** :
  - Détection automatique des sessions CLI sous Windows (`%APPDATA%`), macOS (`~/Library`) et Linux (`~/.config`).
  - Processus d'arrière-plan avec verrouillage PID unique sans doublons (`.companion.lock`).
  - Découverte automatique des écrans GeekMagic sur votre réseau Wi-Fi local.

- **🛡️ Conçu Spécifiquement pour Microcontrôleurs** :
  - **Idempotent** : Calcul d'empreinte SHA-256 évitant les transferts inutiles et préservant la mémoire flash de l'ESP8266/ESP32.
  - **Cœur Immuable** : Pipelines fonctionnels stricts (`@dataclass(frozen=True)`).
  - **Léger en Mémoire** : Encodage JPEG/GIF optimisé pour éviter la saturation des sockets réseau ESP8266.

---

## 📟 Matériel Compatible

| Matériel | Description | Connexion |
|:---|:---|:---|
| **GeekMagic Smart Weather Clock** | Horloge de bureau 240x240 ESP8266 (AliExpress) | Wi-Fi (Mode Photo HTTP) |
| **GeekMagic SmallTV / SmallTV-Pro** | Mini écran météo et multimédia ESP8266 / ESP32 | Wi-Fi (HTTP) |
| **Écran DIY ESP8266 / ESP32** | Cartes de développement avec écran TFT 240x240 | Wi-Fi (HTTP POST) |
| **Écran Virtuel Local** | Génère une image JPG ou GIF en local | Home Assistant / OBS / Web |

---

## 🚀 Démarrage Rapide

### 1. Windows (En 1 Clic)

Double-cliquez sur `start.bat`. Le script effectue tout automatiquement :
1. Vérification de Python et création du `.venv`.
2. Installation des dépendances requises (`pillow`, `requests`).
3. Création automatique de `config.json` avec l'IP de votre écran.
4. Envoi de la première image et démarrage du service d'arrière-plan.

```powershell
git clone https://github.com/neosoda/MiniScreenCompanion.git
cd MiniScreenCompanion
.\start.bat
```

### 2. macOS & Linux

```bash
git clone https://github.com/neosoda/MiniScreenCompanion.git
cd MiniScreenCompanion
chmod +x start.sh && ./start.sh
```

---

## 🛠️ Commandes en Ligne de Commande (CLI)

```bash
# Définir le PYTHONPATH pour l'exécution directe
export PYTHONPATH="src"    # Linux / macOS
$env:PYTHONPATH="src"      # Windows PowerShell

# Envoyer une seule mise à jour et quitter (idéal pour un cron)
python -m mini_screen_companion once

# Démarrer le moniteur continu en arrière-plan
python -m mini_screen_companion run

# Scanner le réseau Wi-Fi local pour trouver l'adresse IP de l'écran
python -m mini_screen_companion discover

# Générer un aperçu local (preview.gif et preview.jpg)
python -m mini_screen_companion preview --open

# Vérifier le statut du service en arrière-plan
python -m mini_screen_companion status

# Arrêter le service d'arrière-plan
python -m mini_screen_companion stop

# Tester avec des données simulées réalistes (sans identifiants)
python -m mini_screen_companion once --demo
```

---

## ⚙️ Configuration (`config.json`)

```json
{
  "screen": {
    "type": "geekmagic",
    "host": "192.168.1.4",
    "port": 80,
    "timeout": 10,
    "brightness": 85
  },
  "display": {
    "mode": "cozy",
    "carousel_page_duration_seconds": 10
  },
  "avatar": {
    "name": "",
    "status": "auto",
    "action": "auto",
    "animated": true,
    "fps": 8,
    "metric": "remaining"
  },
  "polling": {
    "refresh_interval_seconds": 15,
    "retry_delay_seconds": 10
  },
  "providers": {
    "claude": { "enabled": true },
    "codex": { "enabled": true },
    "antigravity": { "enabled": true }
  }
}
```

### Modes d'affichage (`display.mode`)
- `"cozy"` *(Par défaut)* : Ratio 1/3 scène rétro pixel art animée + 2/3 HUD haute lisibilité pour Claude, Codex et Gemini.
- `"summary"` : Résumé épuré avec 3 cartes et doubles jauges 5H / 7J.
- `"carousel"` : Alterne toutes les 10 secondes entre la vue d'ensemble et les jauges géantes par fournisseur.
- `"claude"` / `"codex"` / `"gemini"` : Vue plein écran dédiée au fournisseur choisi.

### Actions de l'Avatar (`avatar.action`)
- `"auto"` *(Par défaut)* : Mode Tamagotchi vivant — adapte les postures en temps réel selon le code, l'heure et les pauses.
- `"desk"` : Développeur au bureau tapant sur son ordinateur avec écran lumineux et café fumant.
- `"coffee"` : Pause détente près de la fenêtre avec tasse de café fumante.
- `"pet"` : Assis au sol caressant le chat roux qui ronronne.
- `"run"` : Petite course dynamique à travers la pièce.
- `"sleep"` : Endormi sur un tapis moelleux sous une couverture avec *z Z z*.

---

## 🏗️ Architecture

```
MiniScreenCompanion/
├── src/mini_screen_companion/
│   ├── core/
│   │   ├── models.py       # Dataclasses immuables (QuotaWindow, ProviderQuota, Snapshot)
│   │   ├── tamagotchi.py   # Machine à états autonome (code, café, chat, course, dodo)
│   │   ├── config.py       # Configuration typée avec valeurs par défaut
│   │   ├── paths.py        # Résolveur cross-platform de caches et tokens CLI
│   │   ├── lock.py         # Verrouillage de processus unique au niveau OS
│   │   └── fonts.py        # Résolveur de typographies avec polices rétro de secours
│   ├── collectors/
│   │   ├── base.py         # Interface abstraite de collecteur
│   │   ├── plugin_cache.py # Parser des tokens de session Claude Code, Codex & Gemini
│   │   └── mock.py         # Collecteur de démonstration déterministe
│   ├── renderers/
│   │   ├── cozy_avatar.py  # Moteur de rendu 1/3 - 2/3 avec doubles jauges
│   │   ├── avatar_sprites.py # Sprites pixel art 16-bit et décor de chambre
│   │   ├── pixel_icons.py  # Icônes rétro 8-bit RGBA pour les IA
│   │   ├── summary.py      # Vue résumé standard multi-cartes
│   │   └── detail.py       # Vue détaillée plein écran par fournisseur
│   └── screens/
│       ├── base.py         # Interface de transport d'écran abstraite
│       ├── geekmagic.py    # Client idempotent pour GeekMagic & ESP8266/ESP32
│       └── local_file.py   # Transport fichier local pour JPG statique et GIF animé
├── assets/                 # Aperçus par défaut, polices et avatars personnalisés
├── tests/                  # Suite de tests sans dépendances externes (13 tests)
├── start.bat               # Lanceur Windows en 1 clic
├── start.sh                # Lanceur Unix
└── config.example.json     # Configuration d'exemple documentée
```

---

## 🧪 Tests Unitaires

La suite de tests s'exécute **sans aucune dépendance externe** :

```bash
$env:PYTHONPATH="src"; python -c "
import tests.test_models as tm, tests.test_collectors as tc, tests.test_renderers as tr, tests.test_cozy_avatar as tca
for m in [tm, tc, tr, tca]:
    for n in dir(m):
        if n.startswith('test_'): getattr(m, n)(); print('PASS:', n)
print('ALL TESTS PASSED!')
"
```

---

## 📄 Licence

Distribué sous la **Licence MIT**. Consultez le fichier `LICENSE` pour plus de détails.  
Copyright &copy; 2026 [neosoda](https://github.com/neosoda).


## 🚧 Living Companion 2.0 — première fondation

- Comportements pilotés par le temps réel (et non par le nombre de rafraîchissements).
- Chat animé indépendant, ambiance jour/nuit et GIF animé en prévisualisation locale.
- Les quotas indisponibles ne sont plus remplacés silencieusement par des pourcentages fictifs : utiliser `--demo` explicitement.
- Sur le firmware constructeur GeekMagic : **JPEG statique uniquement, faute de preuve de prise en charge des GIF animés**. Limite d'envoi par défaut : 300 s, configurable via `screen.min_upload_interval_seconds`.
- Les photos des autres emplacements ne sont plus écrasées.

Détails : [Living Companion V2 — livrables et limites](docs/LIVING_COMPANION_V2.md).
