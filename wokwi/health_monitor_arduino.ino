// Personal Health Monitoring System - Arduino Simulation
// For Wokwi.com online simulator
// This simulates the MAX30102 sensor using potentiometers

#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Pin definitions
const int RED_LED = 7;
const int GREEN_LED = 8;
const int BUTTON = 2;
const int HR_SENSOR = A0;  // Potentiometer 1 simulating heart rate
const int SPO2_SENSOR = A1; // Potentiometer 2 simulating SpO2

// LCD setup (I2C address 0x27, 16 columns, 2 rows)
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Health thresholds
const int HR_MIN = 60;
const int HR_MAX = 100;
const int SPO2_MIN = 95;

// Variables
int heartRate = 0;
int spo2Level = 0;
bool dataLogging = false;
unsigned long lastReadTime = 0;
unsigned long lastSaveTime = 0;
unsigned long buttonPressTime = 0;

// Data storage arrays (simulating cloud storage)
const int MAX_READINGS = 50;
int hrHistory[MAX_READINGS];
int spo2History[MAX_READINGS];
unsigned long timeHistory[MAX_READINGS];
int historyIndex = 0;

void setup() {
  Serial.begin(9600);
  
  // Initialize LCD
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Health Monitor");
  lcd.setCursor(0, 1);
  lcd.print("Initializing...");
  delay(2000);
  
  // Pin modes
  pinMode(RED_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(BUTTON, INPUT_PULLUP);
  
  // Initial LED state
  digitalWrite(RED_LED, LOW);
  digitalWrite(GREEN_LED, LOW);
  
  // Initialize history arrays
  for (int i = 0; i < MAX_READINGS; i++) {
    hrHistory[i] = 0;
    spo2History[i] = 0;
    timeHistory[i] = 0;
  }
  
  Serial.println("=================================");
  Serial.println("Personal Health Monitoring System");
  Serial.println("=================================");
  Serial.println("Adjust potentiometers to simulate:");
  Serial.println("- Pot 1: Heart Rate (40-140 bpm)");
  Serial.println("- Pot 2: Blood Oxygen (85-100%)");
  Serial.println("Press button to save data");
  Serial.println("=================================\n");
}

void loop() {
  // Read sensors every second
  if (millis() - lastReadTime >= 1000) {
    readSensors();
    checkVitals();
    updateDisplay();
    lastReadTime = millis();
  }
  
  // Check button press
  if (digitalRead(BUTTON) == LOW) {
    delay(50); // Debounce
    if (digitalRead(BUTTON) == LOW) {
      buttonPressTime = millis();
      saveDataToCloud();
      while(digitalRead(BUTTON) == LOW && millis() - buttonPressTime < 3000) {
        // Wait for release or timeout
      }
    }
  }
  
  // Auto-save every 60 seconds (simulating daily save)
  if (millis() - lastSaveTime >= 60000) {
    autoSaveData();
    lastSaveTime = millis();
  }
}

void readSensors() {
  // Simulate heart rate (60-120 bpm typical range)
  int hrRaw = analogRead(HR_SENSOR);
  heartRate = map(hrRaw, 0, 1023, 40, 140);
  
  // Simulate SpO2 (85-100% range)
  int spo2Raw = analogRead(SPO2_SENSOR);
  spo2Level = map(spo2Raw, 0, 1023, 85, 100);
  
  // Add some realistic variation
  static int hrVariation = 0;
  hrVariation = (hrVariation + random(-2, 3)) % 5;
  heartRate += hrVariation;
  heartRate = constrain(heartRate, 40, 140);
}

void checkVitals() {
  bool isNormal = (heartRate >= HR_MIN && heartRate <= HR_MAX && spo2Level >= SPO2_MIN);
  
  if (isNormal) {
    digitalWrite(GREEN_LED, HIGH);
    digitalWrite(RED_LED, LOW);
  } else {
    digitalWrite(RED_LED, HIGH);
    digitalWrite(GREEN_LED, LOW);
    
    // Alert message with specific issues
    Serial.print("⚠️  ALERT: ");
    if (heartRate < HR_MIN) {
      Serial.print("Low heart rate! ");
    } else if (heartRate > HR_MAX) {
      Serial.print("High heart rate! ");
    }
    if (spo2Level < SPO2_MIN) {
      Serial.print("Low oxygen level! ");
    }
    Serial.println();
  }
}

void updateDisplay() {
  lcd.clear();
  
  // First line: Heart rate
  lcd.setCursor(0, 0);
  lcd.print("HR:");
  lcd.print(heartRate);
  lcd.print("bpm ");
  
  // Status indicator for HR
  lcd.setCursor(10, 0);
  if (heartRate >= HR_MIN && heartRate <= HR_MAX) {
    lcd.print("[OK]");
  } else if (heartRate < HR_MIN) {
    lcd.print("[LO]");
  } else {
    lcd.print("[HI]");
  }
  
  // Second line: SpO2
  lcd.setCursor(0, 1);
  lcd.print("O2:");
  lcd.print(spo2Level);
  lcd.print("% ");
  
  // Status indicator for SpO2
  lcd.setCursor(10, 1);
  if (spo2Level >= SPO2_MIN) {
    lcd.print("[OK]");
  } else {
    lcd.print("[LOW]");
  }
  
  // Serial output with formatted data
  Serial.print("📊 ");
  Serial.print("HR: ");
  Serial.print(heartRate);
  Serial.print(" bpm");
  
  // Visual indicator in serial
  if (heartRate < HR_MIN || heartRate > HR_MAX) {
    Serial.print(" ⚠️");
  } else {
    Serial.print(" ✓");
  }
  
  Serial.print(" | SpO2: ");
  Serial.print(spo2Level);
  Serial.print("%");
  
  if (spo2Level < SPO2_MIN) {
    Serial.print(" ⚠️");
  } else {
    Serial.print(" ✓");
  }
  
  Serial.println();
}

void saveDataToCloud() {
  // Store data in history
  hrHistory[historyIndex] = heartRate;
  spo2History[historyIndex] = spo2Level;
  timeHistory[historyIndex] = millis() / 1000;
  historyIndex = (historyIndex + 1) % MAX_READINGS;
  
  Serial.println("\n--- 📤 MANUAL SAVE TO CLOUD ---");
  Serial.print("Timestamp: ");
  Serial.print(millis() / 1000);
  Serial.println(" seconds");
  Serial.print("Heart Rate: ");
  Serial.print(heartRate);
  Serial.println(" bpm");
  Serial.print("SpO2: ");
  Serial.print(spo2Level);
  Serial.println("%");
  
  // Simulate cloud API response
  Serial.println("Sending to ThingSpeak...");
  delay(100);
  Serial.println("✅ Data saved successfully!");
  Serial.println("Cloud ID: #" + String(random(1000, 9999)));
  Serial.println("-------------------------------\n");
  
  // Visual feedback on LCD
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Data Saved!");
  lcd.setCursor(0, 1);
  lcd.print("Cloud Upload OK");
  
  // Flash green LED to indicate save
  for (int i = 0; i < 5; i++) {
    digitalWrite(GREEN_LED, HIGH);
    delay(100);
    digitalWrite(GREEN_LED, LOW);
    delay(100);
  }
}

void autoSaveData() {
  Serial.println("\n--- 🔄 AUTO-SAVE (Daily Summary) ---");
  
  // Calculate averages from history
  int validReadings = 0;
  long avgHR = 0;
  long avgSpO2 = 0;
  
  for (int i = 0; i < MAX_READINGS; i++) {
    if (timeHistory[i] > 0) {
      avgHR += hrHistory[i];
      avgSpO2 += spo2History[i];
      validReadings++;
    }
  }
  
  if (validReadings > 0) {
    avgHR /= validReadings;
    avgSpO2 /= validReadings;
    
    Serial.print("Daily Average HR: ");
    Serial.print(avgHR);
    Serial.println(" bpm");
    Serial.print("Daily Average SpO2: ");
    Serial.print(avgSpO2);
    Serial.println("%");
    Serial.print("Total Readings: ");
    Serial.println(validReadings);
  }
  
  Serial.println("✅ Daily summary uploaded");
  Serial.println("-----------------------------------\n");
  
  // Quick LED flash
  digitalWrite(GREEN_LED, HIGH);
  delay(500);
  digitalWrite(GREEN_LED, LOW);
}