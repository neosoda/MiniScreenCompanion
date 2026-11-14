# Firmware Expérimental (Série USB)

Ce dossier contient une ébauche de firmware PlatformIO / Arduino pour microcontrôleur ESP8266 pilotant un écran ST7789 via protocole binaire série USB direct.

> [!WARNING]
> Ce firmware est expérimental. Pour les horloges GeekMagic SmallTV d'origine, le mode HTTP natif avec le firmware constructeur officiel (utilisé par défaut dans `Mini Screen Companion`) est recommandé car les timings de balayage du panneau ST7789 avec broche CS soudée à la masse peuvent provoquer des artéfacts d'affichage sur les firmwares personnalisés.
