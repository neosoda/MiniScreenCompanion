# Living Companion 2.0 — Phase A/B

Work-in-progress foundation for a reliable 240×240 desktop companion.

## Real device vs local preview

- **Factory GeekMagic HTTP firmware:** supports the existing JPEG photo upload
  path. There is **no proof of native GIF playback**, so this driver never
  attempts high-frequency JPEG uploads. It coalesces updates to one every
  `screen.min_upload_interval_seconds` (default **300 seconds**) and leaves
  the other photo slots intact.
- **Local preview:** animated eight-frame GIF; decorative animated cat and
  time-dependent day/night atmosphere. This preview is not evidence of a
  hardware animation capability.
- **Experimental custom firmware:** excluded from the supported production
  path until hardware identification, display timings and rollback are proven.

## Behavior engine

`TamagotchiBrain.update(snapshot, now=...)` uses elapsed time rather than
network poll count. The character codes for a few minutes, then takes
coffee/cat/walking breaks. Real *increases* in 5H quota consumption trigger
a 3-minute focus period. Reused snapshots and quota resets cannot count
as activity. Sleep is automatic 23:00–07:00.

The independent orange cat moves, blinks and breathes without using the
user avatar's animation frames.

## Important limitations / next steps

1. Verify the installed screen model and its firmware upload semantics before
   enabling any higher-frequency animation mechanism.
2. Build non-flash animation delivery only after a transport capability probe.
3. Add a local UI to customize palette, spritesheets, companion actions and
   themes without flashing firmware.
4. Implement a source-freshness indicator for live quota cache entries.

## Development

```powershell
python -m pip install -e ".[dev]"
$env:PYTHONPATH="src"
python -m pytest -q
python -m mini_screen_companion preview --demo
```

Production mode never fabricates quota percentages. Missing providers are
shown as **Donnees indisponibles**. The `--demo` flag remains explicit.


## Visual profiles — in progress

Avatar configuration accepts four added options:

```json
{ "scene": "auto", "palette": "warm", "show_cat": true, "effects": true }
```

Supported scenes: `auto`, `day`, `night`, `rain`. Palettes: `warm`, `mint`, `lavender`. The cat is independent from the avatar. Atmospheric animations are rendered only in the upper 80px area, without touching the quota panel.


## Companion Studio — éditeur local

Lance l'atelier depuis le dossier du projet :

```powershell
$env:PYTHONPATH = "src"
python -m mini_screen_companion studio --demo
```

- Adresse : **http://127.0.0.1:8765/** (aucun accès depuis le LAN).
- Choisir le décor (jour/nuit/pluie), palette, activité, nom, chat et effets.
- Prévisualiser en GIF et exporter le résultat.
- Cliquer sur **Enregistrer le profil** pour écrire uniquement les réglages
  autorisés dans `config.json`. Le fichier est remplacé atomiquement.
- Relancer ensuite le moniteur pour charger les nouveaux réglages.
- Aucun accès au firmware ni envoi Wi-Fi pendant l'utilisation de Studio.

Le mode `--demo` ne simule les quotas que dans l'aperçu ; il n'altère
pas le mode normal.
