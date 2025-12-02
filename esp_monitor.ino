#include <Wire.h>
#include <WiFi.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// === NOTE: Replace these placeholders with your network info locally.
// Do NOT commit real passwords to a PUBLIC repo. ===
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// === URL des endpoints ANVIL ===
// Replace with your real endpoints if needed
const char* URL_ENREGISTRER = "https://example.com/_/api/enregistrer_donnees_capteur";
const char* URL_ALERT_STATUS = "https://example.com/_/api/get_alert_status";

// === Pins ===
const int LED_VERTE_PIN = 15;
const int LED_BLEUE_PIN = 18;
const int LED_ROUGE_PIN = 19;
const int BUZZER_PIN    = 23;

// === I2C et capteurs ===
TwoWire I2C_Bus1 = TwoWire(0);  // GPIO 21/22
TwoWire I2C_Bus2 = TwoWire(1);  // GPIO 4/5
Adafruit_BME280 bme1;
Adafruit_BME280 bme2;

bool capteur1_ok = false;
bool capteur2_ok = false;

void envoyer_donnees_capteur(int sensor_id, float temp, float hum) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(URL_ENREGISTRER);
    http.addHeader("Content-Type", "application/json");
    StaticJsonDocument<200> doc;
    doc["sensor_id"] = sensor_id;
    doc["temperature"] = temp;
    doc["humidite"] = hum;
    String jsonData;
    serializeJson(doc, jsonData);

    Serial.print("📤 Envoi capteur ");
    Serial.print(sensor_id);
    Serial.print(" : ");
    Serial.println(jsonData);

    int codeReponse = http.POST(jsonData);
    String reponse = http.getString();

    Serial.print("📥 Réponse serveur (");
    Serial.print(codeReponse);
    Serial.print(") : ");
    Serial.println(reponse);

    http.end();
  } else {
    Serial.println("❌ WiFi non connecté !");
  }
}

bool get_alert_status() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(URL_ALERT_STATUS);
    int code = http.GET();
    if (code == 200) {
      String response = http.getString();
      StaticJsonDocument<200> doc;
      DeserializationError error = deserializeJson(doc, response);
      http.end();
      if (!error && doc.containsKey("alert")) {
        return doc["alert"];
      }
    } else {
      Serial.print("❌ Erreur GET /get_alert_status : ");
      Serial.println(code);
      http.end();
    }
  }
  return false; // Par défaut, pas d’alerte si erreur réseau
}

void scannerI2C(TwoWire &wire, String busName) {
  Serial.print("\n--- Scan I2C ");
  Serial.print(busName);
  Serial.println(" ---");
  byte count = 0;
  for (byte addr = 1; addr < 127; addr++) {
    wire.beginTransmission(addr);
    byte error = wire.endTransmission();
    if (error == 0) {
      Serial.print("✅ Device trouvé à 0x");
      if (addr < 16) Serial.print("0");
      Serial.print(addr, HEX);
      if (addr == 0x76) Serial.print(" (BME280)");
      if (addr == 0x77) Serial.print(" (BME280)");
      Serial.println();
      count++;
    }
  }
  if (count == 0) Serial.println("❌ Aucun device trouvé");
  else {
    Serial.print("✅ Total: ");
    Serial.print(count);
    Serial.println(" device(s)");
  }
  Serial.println("────────────────────────────");
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("╔═══════════════════════════════════════╗");
  Serial.println("║  Système de monitoring IoT fromagerie ║");
  Serial.println("╚═══════════════════════════════════════╝");

  pinMode(LED_VERTE_PIN, OUTPUT);
  pinMode(LED_BLEUE_PIN, OUTPUT);
  pinMode(LED_ROUGE_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  digitalWrite(LED_VERTE_PIN, HIGH);
  digitalWrite(LED_BLEUE_PIN, LOW);
  digitalWrite(LED_ROUGE_PIN, LOW);
  noTone(BUZZER_PIN);

  // I2C + capteurs
  I2C_Bus1.begin(21, 22, 100000);
  I2C_Bus2.begin(4, 5, 100000);
  scannerI2C(I2C_Bus1, "Bus 1 (GPIO 21/22)");
  scannerI2C(I2C_Bus2, "Bus 2 (GPIO 4/5)");
  capteur1_ok = bme1.begin(0x76, &I2C_Bus1);
  capteur2_ok = bme2.begin(0x76, &I2C_Bus2);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connexion en cours");
  int tentatives = 0;
  while (WiFi.status() != WL_CONNECTED && tentatives < 30) {
    delay(500); Serial.print("."); tentatives++;
  }
  Serial.println();
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("✅ WiFi connecté !");
    Serial.print("Adresse IP : "); Serial.println(WiFi.localIP());
    Serial.print("Signal WiFi : "); Serial.print(WiFi.RSSI()); Serial.println(" dBm");
  } else {
    Serial.println("❌ Échec connexion WiFi !");
  }
  Serial.println("═══════════════════════════════════════");
  Serial.println("     Démarrage du monitoring...");
  Serial.println("═══════════════════════════════\n");
}

void loop() {
  // Vérif connexion WiFi
  if (WiFi.status() == WL_CONNECTED) {
    digitalWrite(LED_BLEUE_PIN, HIGH);
    noTone(BUZZER_PIN);
  } else {
    digitalWrite(LED_BLEUE_PIN, LOW);
    digitalWrite(LED_ROUGE_PIN, HIGH); // Rouge = wifi déconnecté
    noTone(BUZZER_PIN);
    Serial.println("❌ WiFi déconnecté !");
    delay(5000);
    return;
  }

  // Mesures capteurs
  float temp1 = bme1.readTemperature();
  float hum1  = bme1.readHumidity();
  float temp2 = bme2.readTemperature();
  float hum2  = bme2.readHumidity();
  Serial.printf("[BME1] T=%.1f°C H=%.1f%%\n", temp1, hum1);
  Serial.printf("[BME2] T=%.1f°C H=%.1f%%\n", temp2, hum2);

  if (capteur1_ok && !isnan(temp1) && !isnan(hum1)) {
    envoyer_donnees_capteur(1, temp1, hum1);
    delay(1000);
  }
  if (capteur2_ok && !isnan(temp2) && !isnan(hum2)) {
    envoyer_donnees_capteur(2, temp2, hum2);
    delay(1000);
  }

  // Vérifie l’état d’alerte
  bool alerte = get_alert_status();

  // === Séquence alarme ===
  if (alerte) {
    Serial.println("ALERTE : BUZZER & LED ROUGE en séquence ALARME!");

    // 1ère phase : 5s LED clignote + buzzer "beep"
    unsigned long buzzerStart = millis();
    while (millis() - buzzerStart < 5000) {
      digitalWrite(LED_ROUGE_PIN, HIGH);
      tone(BUZZER_PIN, 1200);
      delay(100);
      digitalWrite(LED_ROUGE_PIN, LOW);
      noTone(BUZZER_PIN);
      delay(100);
    }

    // 2e phase : 5s LED clignote seule
    unsigned long ledStart = millis();
    while (millis() - ledStart < 5000) {
      digitalWrite(LED_ROUGE_PIN, HIGH);
      delay(100);
      digitalWrite(LED_ROUGE_PIN, LOW);
      delay(100);
    }

    // On force TOUT off pour garantir l'extinction
    digitalWrite(LED_ROUGE_PIN, LOW);
    noTone(BUZZER_PIN);

    Serial.println("Fin de séquence alarme (tout éteint)");
  } else {
    digitalWrite(LED_ROUGE_PIN, LOW);
    noTone(BUZZER_PIN);
    Serial.println("Statut OK (aucune alerte serveur)");
  }

  delay(1000); // Pause avant la prochaine vérification
}
