//3:46 mod 6, 3:54, 4pm, 4:15, 8:26
#include <Adafruit_Fingerprint.h>
#include <SoftwareSerial.h>

SoftwareSerial mySerial(2, 3); // RX, TX
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);

void setup() {
  Serial.begin(9600);
  while (!Serial);
  delay(100);
  Serial.println("Fingerprint system ready.");

  finger.begin(57600);
  if (finger.verifyPassword()) {
    Serial.println("Sensor detected!");
  } else {
    Serial.println("Sensor not found :(");
    while (1) { delay(1); }
  }

  Serial.println("Commands:");
  Serial.println("1,<id> - Enroll fingerprint");
  Serial.println("2 - Search fingerprint");
  Serial.println("3,<id> - Delete fingerprint");
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    if (command.length() == 0) return;

    char cmdType = command.charAt(0);
    int id = -1;
    if (command.indexOf(',') > 0) {
      id = command.substring(command.indexOf(',') + 1).toInt();
    }

    if (cmdType == '1' && id > 0) {
      Serial.print("[CMD] Enroll ID ");
      Serial.println(id);
      enrollFingerprint(id);
    } else if (cmdType == '2') {
      Serial.println("[CMD] Search Fingerprint");
      getFingerprintID();
    } else if (cmdType == '3' && id > 0) {
      Serial.print("[CMD] Delete ID ");
      Serial.println(id);
      deleteFingerprint(id);
    } else {
      Serial.println("[ERR] Invalid command format");
    }
  }
}

// ===== Fingerprint Functions =====

void enrollFingerprint(int id) {
  Serial.println("Place your finger...");
  int p = -1;
  while (p != FINGERPRINT_OK) { p = finger.getImage(); }

  p = finger.image2Tz(1);
  if (p != FINGERPRINT_OK) { Serial.println("Error converting image"); return; }

  Serial.println("Remove finger");
  delay(2000);
  while (finger.getImage() != FINGERPRINT_NOFINGER);

  Serial.println("Place same finger again...");
  while (finger.getImage() != FINGERPRINT_OK);

  p = finger.image2Tz(2);
  if (p != FINGERPRINT_OK) { Serial.println("Error converting second image"); return; }

  p = finger.createModel();
  if (p != FINGERPRINT_OK) { Serial.println("Error creating model"); return; }

  p = finger.storeModel(id);
  if (p == FINGERPRINT_OK) {
    Serial.print("✅ Fingerprint ID #");
    Serial.print(id);
    Serial.println(" stored successfully!");
  } else {
    Serial.print("❌ Failed to store fingerprint ID #");
    Serial.println(id);
  }
}

void getFingerprintID() {
  Serial.println("Place your finger...");
  int p = finger.getImage();
  if (p != FINGERPRINT_OK) { Serial.println("No finger detected"); return; }

  p = finger.image2Tz();
  if (p != FINGERPRINT_OK) { Serial.println("Error converting image"); return; }

  p = finger.fingerFastSearch();
  if (p == FINGERPRINT_OK) {
    Serial.print("Match found! ID: ");
    Serial.print(finger.fingerID);
    Serial.print("  Confidence: ");
    Serial.println(finger.confidence);
  } else {
    Serial.println("No match found.");
  }
}

void deleteFingerprint(int id) {
  uint8_t p = finger.deleteModel(id);
  if (p == FINGERPRINT_OK) {
    Serial.print("✅ Fingerprint ID #");
    Serial.print(id);
    Serial.println(" deleted successfully!");
  } else {
    Serial.print("❌ Failed to delete fingerprint ID #");
    Serial.print(id);
    Serial.print(". Error code: ");
    Serial.println(p);
  }
}
