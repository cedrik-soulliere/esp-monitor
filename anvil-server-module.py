# Anvil server module (paste into anvil/server_module.py in the repo)
# NOTE: Do NOT commit any real UPLINK_KEY, API keys or secrets to the repo.

import anvil.server
import anvil.email
import anvil.tables as tables
from anvil.tables import app_tables
from datetime import datetime
import pytz
import json
import time
import anvil.users

ALERT_LAST_SENT = {}

# ====== GESTION DU MOT DE PASSE UTILISATEUR ======
@anvil.server.callable
def reset_user_password(new_pwd):
  try:
    anvil.users.change_password(new_pwd)  # Auth natif Anvil
    return True
  except Exception as e:
    print(f"Erreur : {e}")
    return False

# ====== GESTION DES PREFERENCES DE NOTIFICATION ======
@anvil.server.callable
def set_notification_prefs(prefs):
  row = app_tables.notification_prefs.search()
  row = list(row)[0] if row else app_tables.notification_prefs.add_row()
  for key in prefs:
    row[key] = prefs[key]

@anvil.server.callable
def get_notification_prefs():
  rows = app_tables.notification_prefs.search()
  if rows:
    r = list(rows)[0]
    return {
      "notif_temp": bool(r['notif_temp']),
      "notif_hum": bool(r['notif_hum']),
      "notif_disconnect": bool(r['notif_disconnect']),
      "notif_schedule": r['notif_schedule'],
      "last_notif_sent": r['last_notif_sent']
    }
  return {
    "notif_temp": True,
    "notif_hum": True,
    "notif_disconnect": True,
    "notif_schedule": "30 minutes",
    "last_notif_sent": None
  }

# ====== GESTION DES SEUILS ======
@anvil.server.callable
def set_live_sensor_limits(min_temp=None, max_temp=None, min_hum=None, max_hum=None):
  seuils = app_tables.seuils.search()
  row = list(seuils)[0] if seuils else app_tables.seuils.add_row()
  if min_temp is not None: row['min_temp'] = min_temp
  if max_temp is not None: row['max_temp'] = max_temp
  if min_hum is not None: row['min_hum'] = min_hum
  if max_hum is not None: row['max_hum'] = max_hum

@anvil.server.callable
def get_live_sensor_limits():
  seuils = app_tables.seuils.search()
  if seuils:
    row = list(seuils)[0]
    return {
      "min_temp": row['min_temp'],
      "max_temp": row['max_temp'],
      "min_hum": row['min_hum'],
      "max_hum": row['max_hum']
    }
  return {
    "min_temp": 15,
    "max_temp": 30,
    "min_hum": 20,
    "max_hum": 60
  }

@anvil.server.callable
def enregistrer_donnees_capteur(sensor_id, temperature, humidite):
  try:
    est = pytz.timezone('America/New_York')
    timestamp_est = datetime.now(est)
    app_tables.donnees_capteurs.add_row(
      sensor_id=sensor_id,
      temperature=temperature,
      humidite=humidite,
      timestamp=timestamp_est
    )
    verifier_seuils_et_alerter(sensor_id, temperature, humidite)
    return {"status": "success", "message": "Donnees enregistrees"}
  except Exception as e:
    print(f"Erreur lors de l'enregistrement : {e}")
    return {"status": "error", "message": str(e)}

@anvil.server.http_endpoint("/enregistrer_donnees_capteur", methods=["POST"], enable_cors=True)
def http_enregistrer_donnees_capteur():
  try:
    request_body = anvil.server.request.body_json
    if not request_body:
      return json.dumps({"status": "error", "message": "Pas de données JSON reçues"})
    sensor_id = int(request_body.get('sensor_id', 0))
    temperature = float(request_body.get('temperature', 0))
    humidite = float(request_body.get('humidite', 0))
    print(f"✅ Reçu de l'ESP32: Capteur {sensor_id}, T={temperature}°C, H={humidite}%")
    resultat = enregistrer_donnees_capteur(sensor_id, temperature, humidite)
    print(f"✅ Résultat enregistrement: {resultat}")
    return json.dumps(resultat)
  except Exception as e:
    error_msg = f"❌ Erreur HTTP endpoint: {str(e)}"
    print(error_msg)
    import traceback
    traceback.print_exc()
    return json.dumps({"status": "error", "message": error_msg})

def verifier_seuils_et_alerter(sensor_id, temperature, humidite):
  seuils = get_live_sensor_limits()
  prefs = get_notification_prefs()
  alertes = []
  if prefs.get("notif_temp", True):
    if temperature < seuils["min_temp"]:
      alertes.append(f"Température: {temperature:.1f}°C (< {seuils['min_temp']}°C)")
    elif temperature > seuils["max_temp"]:
      alertes.append(f"Température: {temperature:.1f}°C (> {seuils['max_temp']}°C)")
  if prefs.get("notif_hum", True):
    if humidite < seuils["min_hum"]:
      alertes.append(f"Humidité: {humidite:.1f}% (< {seuils['min_hum']}%)")
    elif humidite > seuils["max_hum"]:
      alertes.append(f"Humidité: {humidite:.1f}% (> {seuils['max_hum']}%)")
  if alertes:
    now = time.time()
    last_sent = ALERT_LAST_SENT.get(sensor_id, 0)
    cooldown = 600
    if now - last_sent > cooldown:
      ALERT_LAST_SENT[sensor_id] = now
      message = (
        "Attention : courriel externe | external email\n\n"
        + "Les capteurs suivants sont hors du seuil sélectionné:\n\n"
        + f"• Sensor {sensor_id} — " + ", ".join(alertes)
      )
      send_summary_alert("csoul040@uottawa.ca", message)
      row = app_tables.notification_prefs.search()
      if row:
        list(row)[0]['last_notif_sent'] = datetime.now()
      print(f"Email sent for sensor {sensor_id} at {datetime.now()}")
    else:
      print(f"No email sent for capteur {sensor_id}: cooldown active ({int(now-last_sent)}s since last alert)")

@anvil.server.callable
def obtenir_dernieres_donnees():
  try:
    resultats = {}
    for sensor_id in [1, 2]:
      donnees = app_tables.donnees_capteurs.search(
        tables.order_by("timestamp", ascending=False),
        sensor_id=sensor_id
      )
      if len(donnees) > 0:
        derniere = donnees[0]
        resultats[f"capteur{sensor_id}"] = {
          'temp': derniere['temperature'],
          'humid': derniere['humidite'],
          'timestamp': derniere['timestamp']
        }
      else:
        resultats[f"capteur{sensor_id}"] = None
    return resultats
  except Exception as e:
    print(f"Erreur lors de la récupération des données : {e}")
    return {}

@anvil.server.callable
def get_all_capteur_rows(n=100):
  try:
    rows = app_tables.donnees_capteurs.search(
      tables.order_by('timestamp', ascending=False)
    )
    output = []
    for i, row in enumerate(rows):
      if i >= n: break
      d = dict(row)
      if "timestamp" in d and d["timestamp"]:
        d["timestamp"] = d["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
      output.append(d)
    return output
  except Exception as e:
    print(f"Erreur récupération données capteurs: {e}")
    import traceback
    traceback.print_exc()
    return []

@anvil.server.callable
def send_summary_alert(email, body):
  try:
    anvil.email.send(
      to=email,
      subject="⚠️ Alerte système des capteurs",
      text=body
    )
  except Exception as e:
    print(f"Email failed: {e}")

@anvil.server.http_endpoint("/get_alert_status", methods=["GET"], enable_cors=True)
def get_alert_status():
  try:
    rows = app_tables.donnees_capteurs.search(
      tables.order_by("timestamp", ascending=False)
    )
    if len(rows) > 0:
      row = rows[0]
      temperature = row['temperature']
      humidite = row['humidite']
      seuils = get_live_sensor_limits()
      alert = (
        temperature < seuils["min_temp"]
        or temperature > seuils["max_temp"]
        or humidite < seuils["min_hum"]
        or humidite > seuils["max_hum"]
      )
      return json.dumps({"alert": alert})
    else:
      return json.dumps({"alert": False})
  except Exception as e:
    print(f"Erreur get_alert_status: {e}")
    return json.dumps({"alert": False})
