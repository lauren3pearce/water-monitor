#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Initialize LCD with I2C address
LiquidCrystal_I2C lcd(0x27, 16, 2); 

int waterSensorPin = A0; // Water Sensor connected to pin A0
int conductivityPin = A1;  // Conductivity sensor signal pin
int ledPin = 13; // Water sensor LED connected to digital pin 13
int conductivityLedPin = 11; // Conductivity LED connected to digital pin 11

// Conductivity thresholds
const int conductivityMin = 100;
const int conductivityMax = 400;

void setup() {
  Serial.begin(9600); // Initialize serial communication

  // Initialize LCD
  lcd.init();
  lcd.backlight(); // Turn on LCD backlight
  lcd.setCursor(0, 0);
  lcd.print("Water System");
  delay(2000); // Show startup message
  lcd.clear();

  // Set pins as output
  pinMode(ledPin, OUTPUT);
  pinMode(conductivityLedPin, OUTPUT);
}

void loop() {
  // Read sensor values
  int waterLevel = analogRead(waterSensorPin);
  int conductivity = analogRead(conductivityPin);

  // Print to Serial Monitor for debugging
  Serial.print("Water Level: ");
  Serial.println(waterLevel);
  Serial.print("Conductivity: ");
  Serial.println(conductivity);

  // Display readings on LCD
  lcd.setCursor(0, 0); // First line
  lcd.print("Level: ");
  lcd.print(waterLevel);
  lcd.print("     "); // Clear extra characters if any remain

  lcd.setCursor(0, 1); // Second line
  lcd.print("Cond: ");
  lcd.print(conductivity);
  lcd.print("     "); // Clear extra characters if any remain

  // Water level monitoring logic
  if (waterLevel > 400) {
    digitalWrite(ledPin, HIGH);  // Turn on water level LED
  } else {
    digitalWrite(ledPin, LOW);   // Turn off water level LED
  }

  // Conductivity monitoring logic
  if (conductivity < conductivityMin || conductivity > conductivityMax) {
    digitalWrite(conductivityLedPin, HIGH); // Turn on conductivity LED
  } else {
    digitalWrite(conductivityLedPin, LOW);  // Turn off conductivity LED
  }

  delay(1000); // Wait before next reading
}
