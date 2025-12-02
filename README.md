# esp-monitor — Projet IoT (ESP32) + Interface Anvil

Ce dépôt rassemble le code de l'application de monitoring IoT (ESP32) et les modules Anvil pour l'interface web.  
Le but : collecter des mesures de capteurs (température / humidité), stocker et alerter, et fournir une interface web pour visualiser et configurer.

---

## Contenu du dépôt (fichiers principaux)
- README.md — (ce fichier) index et instructions.
- esp_monitor.ino — Sketch Arduino / ESP32 (ESP32 + BME280, envoi des données vers l'API).
- anvil-server-module.py (ou anvil-server-module.py selon ton commit) — logique serveur : endpoints HTTP, sauvegarde en Data Tables, envoi d'emails, alertes.
- capteurs_form.py — code du Form principal (UI) pour affichage des capteurs / heatmaps / graphique.
- parametre_form.py — page Paramètres (seuils, préférences de notification, changement de mot de passe).
- logout_form.py — Form de gestion login/logout.
- frame_form.py — Frame principal qui gère la navigation entre forms.

Liens directs (copier/coller pour le correcteur)
- Page racine du dépôt : https://github.com/cedrik-soulliere/esp-monitor
- Sketch ESP32 : https://github.com/cedrik-soulliere/esp-monitor/blob/main/esp_monitor.ino
- Module serveur Anvil : https://github.com/cedrik-soulliere/esp-monitor/blob/main/anvil-server-module.py
- Form Capteurs : https://github.com/cedrik-soulliere/esp-monitor/blob/main/capteurs_form.py
- Form Paramètres : https://github.com/cedrik-soulliere/esp-monitor/blob/main/parametre_form.py
- Form Logout : https://github.com/cedrik-soulliere/esp-monitor/blob/main/logout_form.py
- Frame principal : https://github.com/cedrik-soulliere/esp-monitor/blob/main/frame_form.py

> Remarque : si certains fichiers sont dans un sous-dossier (ex. `anvil/`), remplace `blob/main/<filename>` par `blob/main/anvil/<filename>`.

---

## Comment le correcteur peut lire / télécharger le projet
- Ouvrir le lien racine (ci‑dessus) et cliquer sur les fichiers listés.
- Pour télécharger l'ensemble en ZIP : bouton vert "Code" → "Download ZIP".
- Pour un lien direct vers un fichier précis (montrer un extrait dans le devoir), utiliser les liens "blob" fournis ci‑dessus.

---

## Exécution / tests (guides rapides)

### 1) ESP32 (esp_monitor.ino)
1. Ouvrir `esp_monitor.ino` dans l'Arduino IDE (ou PlatformIO).
2. Avant d'uploader sur l'ESP32 : ne laissez pas de mot de passe en clair dans le dépôt public.
   - Remplacez `WIFI_SSID` / `WIFI_PASSWORD` par vos valeurs localement, ou
   - Mettez ces infos dans un fichier `secrets.h` (ajouté à `.gitignore`) et incluez‑le localement.
3. Installer les bibliothèques nécessaires dans l'IDE Arduino :
   - Adafruit BME280
   - Adafruit Unified Sensor
   - ArduinoJson
   - (ESP32 core fournit `WiFi` et `HTTPClient`)
4. Sélectionner la carte ESP32 correcte puis "Upload".

Si vous testez les endpoints HTTP (depuis l'ESP ou via curl/Postman), vérifiez que l'URL dans le sketch pointe vers le bon endpoint (celui fourni par Anvil / autre serveur).

---

### 2) Anvil (modules client + serveur)
- Les fichiers `*_form.py` sont des exports des Form d'Anvil (logique Python du client).
- `anvil-server-module.py` est le code serveur (endpoints, enregistrement en Data Tables, envoi d'emails, etc.).

Pour exécuter / tester l'app Anvil réellement :
1. Ouvrir l'IDE Anvil (https://anvil.works) et créer un nouveau projet.
2. Copier/Coller les modules :
   - Créer les Server Modules et coller le contenu de `anvil-server-module.py`.
   - Créer les Forms et coller les fichiers correspondants (`capteurs_form.py`, `parametre_form.py`, `logout_form.py`, `frame_form.py`). Note : les fichiers `. _anvil_designer` (layout généré par Anvil) ne sont pas inclus ici ; pour tester l'UI il faut recréer les composants ou importer un export complet depuis Anvil.
3. Configurer les Data Tables (les tables utilisées : `donnees_capteurs`, `seuils`, `notification_prefs`, etc.) avec les colonnes attendues.
4. Configurer l'envoi d'email via Anvil (si utilisé).
5. (Optionnel) Pour des scripts Uplink locaux : créer un fichier `secrets.py` local avec la clé `UPLINK_KEY` et exécuter `python uplink_script.py` (ne pas commit la clé).

---

## Structure recommandée (si tu veux organiser)
- racine/
  - README.md
  - esp_monitor.ino
  - anvil-server-module.py
  - capteurs_form.py
  - parametre_form.py
  - logout_form.py
  - frame_form.py
  - .gitignore

Tu peux aussi regrouper les modules Anvil dans un dossier `anvil/` si tu préfères (ex. `anvil/capteurs_form.py`).

---

## Sécurité — IMPORTANT
- NE JAMAIS committer de secrets : UPLINK_KEY, mots de passe Wi‑Fi, clé API, etc.
- Utilise `secrets.example` pour montrer le format, et ajoute `secrets.py` dans `.gitignore`.
- Si tu as accidentellement poussé une clé, dis‑le moi : je t'aide à la retirer de l'historique Git en toute sécurité.

---

## Liens utiles pour corriger / pour l'enseignant
- Lien racine (tout voir) : https://github.com/cedrik-soulliere/esp-monitor
- Lien direct au sketch ESP32 : https://github.com/cedrik-soulliere/esp-monitor/blob/main/esp_monitor.ino
- Lien direct au module serveur : https://github.com/cedrik-soulliere/esp-monitor/blob/main/anvil-server-module.py
- Lien direct au Form principal : https://github.com/cedrik-soulliere/esp-monitor/blob/main/capteurs_form.py

---

## Permalink (verrouiller une version)
Si tu veux que le correcteur voie exactement le code que tu as remis (même si tu modifies le repo après) :
1. Ouvre le fichier sur GitHub.
2. Clique "History" en haut du fichier.
3. Ouvre le commit correspondant et copie l'URL depuis la barre d'adresse — elle contient le SHA du commit et restera fixe.

---

## Notes finales / Contact
- Auteur : cedrik-soulliere  
