#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h>
#include <SoftwareSerial.h>
#include <Adafruit_Fingerprint.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <time.h>

// WiFi credentials
const char* ssid = "Megatron";
const char* password = "HYPOTHESIS786@";
// const char* ssid = "Whitefield School";
// const char* password = "CLB@1096";

// Base IP and Port
// #define SERVER_IP "192.168.1.37"
#define SERVER_IP "192.168.1.17"

#define BASE_URL "http://" SERVER_IP ":5000"

// Flask server endpoints
const char* enrollURL      = BASE_URL "/enroll";
const char* enrollDoneURL  = BASE_URL "/enroll_done";
const char* deleteURL      = BASE_URL "/delete";
const char* deleteDoneURL  = BASE_URL "/delete_done";
const char* logURL         = BASE_URL "/log";
const char* pingURL        = BASE_URL "/ping";


// OLED display
Adafruit_SH1106G display(128, 64, &Wire, -1);

// Fingerprint sensor
SoftwareSerial fingerSerial(D5, D6); // RX, TX
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&fingerSerial);

// Timers
unsigned long lastModeCheck = 0;
unsigned long lastEnrollCheck = 0;
unsigned long lastDeleteCheck = 0;

const unsigned long modeInterval = 5000;
const unsigned long enrollInterval = 15000;
const unsigned long deleteInterval = 20000;

WiFiClient client;

void setup() {
  Serial.begin(115200);
  finger.begin(57600);

  display.begin(0x3C, true);
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SH110X_WHITE);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("Connecting WiFi...");
    display.display();
  }

  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("WiFi Connected!");

  if (finger.verifyPassword()) {
    display.setCursor(0, 20);
    display.println("Sensor Ready");
  } else {
    display.setCursor(0, 20);
    display.println("Sensor Error");
  }
  display.display();

  // Sync time via NTP (Nepal = UTC+5:45 = 19800 seconds)
  configTime(19800, 0, "pool.ntp.org");
}

void loop() {
  unsigned long now = millis();

  if (now - lastModeCheck > modeInterval) {
    showMode();
    lastModeCheck = now;
  }

  if (now - lastEnrollCheck > enrollInterval) {
    checkEnrollQueue();
    lastEnrollCheck = now;
  }

  if (now - lastDeleteCheck > deleteInterval) {
    checkDeleteQueue();
    lastDeleteCheck = now;
  }

  checkFingerprint();
}

void showMode() {
  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("Mode: Attendance");
  display.display();
}

void checkEnrollQueue() {
  if (WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;
  http.begin(client, enrollURL);
  int code = http.GET();

  if (code == 200) {
    String ids = http.getString();
    if (ids.length() > 0) {
      enrollList(ids);
    }
  }
  http.end();
}

void checkDeleteQueue() {
  if (WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;
  http.begin(client, deleteURL);
  int code = http.GET();

  if (code == 200) {
    String ids = http.getString();
    if (ids.length() > 0) {
      deleteList(ids);
    }
  }
  http.end();
}

void enrollList(String ids) {
  while (ids.length() > 0) {
    int comma = ids.indexOf(',');
    int id = (comma == -1) ? ids.toInt() : ids.substring(0, comma).toInt();
    ids = (comma == -1) ? "" : ids.substring(comma + 1);

    bool ok = enrollFingerprint(id);

    display.clearDisplay();
    display.setCursor(0, 0);
    if (ok) {
      display.print("Enrolled ID: ");
      display.println(id);
      notifyEnrollDone(id);
    } else {
      display.print("Enroll Failed: ");
      display.println(id);
    }
    display.display();
    delay(2000);
  }
}

bool enrollFingerprint(uint8_t id) {
  int p = -1;

  // STEP 1: First scan
  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("Place finger...");
  display.display();

  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
    if (p == FINGERPRINT_NOFINGER) continue;
    if (p == FINGERPRINT_PACKETRECIEVEERR) return false;
    if (p == FINGERPRINT_IMAGEFAIL) return false;
  }

  if (finger.image2Tz(1) != FINGERPRINT_OK) return false;

  // STEP 2: Remove finger
  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("Remove finger...");
  display.display();
  delay(2000);

  // STEP 3: Second scan
  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("Place again...");
  display.display();

  p = -1;
  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
    if (p == FINGERPRINT_NOFINGER) continue;
    if (p == FINGERPRINT_PACKETRECIEVEERR) return false;
    if (p == FINGERPRINT_IMAGEFAIL) return false;
  }

  if (finger.image2Tz(2) != FINGERPRINT_OK) return false;

  // STEP 4: Create model
  p = finger.createModel();
  if (p == FINGERPRINT_ENROLLMISMATCH) {
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("Finger mismatch!");
    display.display();
    return false;
  }
  if (p != FINGERPRINT_OK) return false;

  // STEP 5: Store model
  p = finger.storeModel(id);
  if (p != FINGERPRINT_OK) {
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("Store failed!");
    display.display();
    return false;
  }

  return true;
}


void notifyEnrollDone(int id) {
  HTTPClient http;
  http.begin(client, enrollDoneURL);
  http.addHeader("Content-Type", "application/json");

  String body = "{\"finger_id\":" + String(id) + "}";
  http.POST(body);
  http.end();
}

void deleteList(String ids) {
  while (ids.length() > 0) {
    int comma = ids.indexOf(',');
    int id = (comma == -1) ? ids.toInt() : ids.substring(0, comma).toInt();
    ids = (comma == -1) ? "" : ids.substring(comma + 1);

    finger.deleteModel(id);

    display.clearDisplay();
    display.setCursor(0, 0);
    display.print("Deleted ID: ");
    display.println(id);
    display.display();

    notifyDeleteDone(id);
    delay(1500);
  }
}

void notifyDeleteDone(int id) {
  HTTPClient http;
  http.begin(client, deleteDoneURL);
  http.addHeader("Content-Type", "application/json");

  String body = "{\"finger_id\":" + String(id) + "}";
  http.POST(body);
  http.end();
}

void checkFingerprint() {
  if (finger.getImage() != FINGERPRINT_OK) return;
  if (finger.image2Tz() != FINGERPRINT_OK) return;
  if (finger.fingerSearch() != FINGERPRINT_OK) return;

  int id = finger.fingerID;

  display.clearDisplay();
  display.setCursor(0, 0);
  display.print("Welcome ID: ");
  display.println(id);
  display.display();

  sendAttendance(id);
  delay(2000);
}

void sendAttendance(int id) {
  if (WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;
  http.begin(client, logURL);

  String timestamp = getTimestamp();
  String payload = "{\"finger_id\":" + String(id) + ",\"timestamp\":\"" + timestamp + "\"}";

  http.addHeader("Content-Type", "application/json");
  http.POST(payload);
  http.end();
}

String getTimestamp() {
  time_t now = time(nullptr);
  struct tm* t = localtime(&now);
  char buf[20];
  sprintf(buf, "%04d-%02d-%02d %02d:%02d:%02d",
          t->tm_year + 1900,
          t->tm_mon + 1,
          t->tm_mday,
          t->tm_hour,
          t->tm_min,
          t->tm_sec);
  return String(buf);
}
