#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

#define SENSOR_PIN A2
#define WET_THRESHOLD 210
#define DRY_THRESHOLD 510
#define BUZZER_PIN 11
#define HUMIDITY_ALERT 60

void setup() {
    pinMode(BUZZER_PIN, OUTPUT);
    digitalWrite(BUZZER_PIN, LOW);

    Serial.begin(9600);
    lcd.init();
    lcd.backlight();

    // Mensaje inicial
    lcd.setCursor(0, 0);
    lcd.print("DryWall System");
    lcd.setCursor(0, 1);
    lcd.print("Initializing...");
    delay(2000);
    lcd.clear();
}

void loop() {
    int value = analogRead(SENSOR_PIN);
    int pct = map(value, WET_THRESHOLD, DRY_THRESHOLD, 100, 0);
    pct = constrain(pct, 0, 100);

    // Mostrar en LCD
    lcd.setCursor(0, 0);
    lcd.print("Moisture: ");
    lcd.print(pct);
    lcd.print("%   ");

    lcd.setCursor(0, 1);
    lcd.print("Raw: ");
    lcd.print(value);
    lcd.print("    ");

    // Enviar por Serial (formato compatible con Python)
    Serial.print("Raw: ");
    Serial.print(value);
    Serial.print("  |  H2O%: ");
    Serial.print(pct);
    Serial.println("%");

    // Alarma
    if (pct >= HUMIDITY_ALERT) {
        tone(BUZZER_PIN, 3000);
    } else {
        noTone(BUZZER_PIN);
    }

    delay(500); // Enviar datos cada segundo
}