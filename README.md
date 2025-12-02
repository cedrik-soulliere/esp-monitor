# esp-monitor — Index des projets

Ce dépôt regroupe les travaux du projet IoT / Anvil.

Résumé
- C++ (ESP32) : code pour l’ESP32 / capteurs — dossier `cpp/` ou fichier `esp_monitor.ino`
- Anvil : code client et serveur pour l’interface web — dossier `anvil/`
- Python : (si tu as des scripts Python) dossier `python/`

Comment naviguer
- Ouvre ce dépôt : https://github.com/cedrik-soulliere/esp-monitor
- Cliquez sur les dossiers listés ci‑dessous pour accéder aux sources :
  - Anvil (interface & server) : `anvil/`
  - ESP32 (sketch) : `cpp/` ou `esp_monitor.ino`
  - Python scripts : `python/` (si présent)

Raccourcis directs (exemples)
- Form principal (Capteurs) : `anvil/capteurs_form.py`
- Module serveur Anvil : `anvil/server_module.py`
- ESP32 sketch : `esp_monitor.ino`

Notes importantes
- Ne pas committer de secrets (mots de passe, clés UPLINK, API keys). Voir `anvil/secrets.example`.
- Pour exécuter chaque projet, ouvrir le README présent dans le dossier correspondant pour les commandes et dépendances.

Contact
- Auteur : cedrik-soulliere
