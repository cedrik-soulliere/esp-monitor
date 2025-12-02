from ._anvil_designer import ParametreTemplate
from anvil import *
import anvil.server

class Parametre(ParametreTemplate):

  def __init__(self, **properties):
    self.init_components(**properties)
    self.user = anvil.users.get_user()
    self.label_email.text = self.user['email'] if self.user else "Non connecté"
    self.drop_down_1.items = [
      "10 minutes", "30 minutes", "1 heure", "2 heures",
      "6 heures", "12 heures", "24 heures", "48 heures",
      "1 semaine", "2 semaines"
    ]
    self.load_seuils_from_server()
    self.load_last_notif_sent()
    self.load_notification_prefs()  # ← Ajouté !

    # Charger les seuils depuis le serveur sur l'UI
  def load_seuils_from_server(self):
    seuils = anvil.server.call('get_live_sensor_limits')
    self.min_temp_box.text = str(seuils['min_temp'])
    self.max_temp_box.text = str(seuils['max_temp'])
    self.min_hum_box.text = str(seuils['min_hum'])
    self.max_hum_box.text = str(seuils['max_hum'])

  def save_all_seuils(self, **event_args):
    try:
      min_temp = float(self.min_temp_box.text)
      max_temp = float(self.max_temp_box.text)
      min_hum = float(self.min_hum_box.text)
      max_hum = float(self.max_hum_box.text)
      anvil.server.call('set_live_sensor_limits',
                        min_temp=min_temp, max_temp=max_temp,
                        min_hum=min_hum, max_hum=max_hum)
      Notification(
        f"Seuils sauvegardés ! Température : {min_temp}–{max_temp} °C | Humidité : {min_hum}–{max_hum} %"
      ).show()
      self.load_last_notif_sent()
    except Exception as e:
      alert(f"Erreur de saisie (valeur ou connexion) : {e}")

  def load_last_notif_sent(self):
    notif_prefs = anvil.server.call('get_notification_prefs')
    last_dt = notif_prefs.get("last_notif_sent")
    if last_dt:
      txt = f"Dernière notification envoyée : {last_dt.strftime('%d %b %Y, %H:%M')}"
    else:
      txt = "Dernière notification envoyée : Aucune"
    self.label_last_notif.text = txt

    # --- Mot de passe : bouton ou touche ENTER ---
  def mot_de_passe_pressed_enter(self, **event_args):
    self.reset_user_password()

  def reset_mdp_button_click(self, **event_args):
    self.reset_user_password()

  def reset_user_password(self):
    if not self.user:
      alert("Aucun utilisateur connecté.")
      return
    new_pwd = self.mot_de_passe.text
    if not new_pwd:
      alert("Entrez un nouveau mot de passe.")
      return
    try:
      import anvil.users
      anvil.users.change_password(new_pwd)
      Notification("Mot de passe mis à jour !").show()
      self.mot_de_passe.text = ""
    except Exception as e:
      alert(f"Erreur lors du changement du mot de passe : {e}")

    # --- Gestion des préférences notifications ---
  def load_notification_prefs(self):
    prefs = anvil.server.call('get_notification_prefs')
    # Adapte les noms de widgets selon ceux de ton designer
    self.check_box_1.checked = prefs.get("notif_temp", True)
    self.check_box_2.checked = prefs.get("notif_hum", True)
    self.check_box_4.checked = prefs.get("notif_disconnect", True)
    self.drop_down_1.selected_value = prefs.get("notif_schedule", "30 minutes")

  def save_notification_prefs(self, **event_args):
    prefs = {
      "notif_temp": self.check_box_1.checked,
      "notif_hum": self.check_box_2.checked,
      "notif_disconnect": self.check_box_4.checked,
      "notif_schedule": self.drop_down_1.selected_value
    }
    anvil.server.call('set_notification_prefs', prefs)
    Notification("Préférences de notifications sauvegardées !").show()

    # Méthodes “change” qui sauvegardent dès changement
  def check_box_1_change(self, **event_args):
    self.save_notification_prefs()
  def check_box_2_change(self, **event_args):
    self.save_notification_prefs()
  def check_box_4_change(self, **event_args):
    self.save_notification_prefs()
  def drop_down_1_change(self, **event_args):
    self.save_notification_prefs()
  def drop_down_1_show(self, **event_args):
    pass  # Optionnel mais évite warning

    # -- Events pour update immédiat (ENTER) sur les seuils
  def min_temp_box_pressed_enter(self, **event_args):
    self.save_all_seuils()
  def max_temp_box_pressed_enter(self, **event_args):
    self.save_all_seuils()
  def min_hum_box_pressed_enter(self, **event_args):
    self.save_all_seuils()
  def max_hum_box_pressed_enter(self, **event_args):
    self.save_all_seuils()
  def save_button_click(self, **event_args):
    self.save_all_seuils()
