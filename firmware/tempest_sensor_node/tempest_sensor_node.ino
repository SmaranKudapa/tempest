#include <DHT.h>
#include <LiquidCrystal.h>

const int DHT_PIN = 2;
const int DHT_TYPE = DHT11;

const int LCD_RS = 7;
const int LCD_ENABLE = 8;
const int LCD_D4 = 3;
const int LCD_D5 = 4;
const int LCD_D6 = 5;
const int LCD_D7 = 6;

const unsigned long READ_INTERVAL_MS = 2000;
const unsigned long SERIAL_BAUD_RATE = 9600;

DHT dht(DHT_PIN, DHT_TYPE);
LiquidCrystal lcd(LCD_RS, LCD_ENABLE, LCD_D4, LCD_D5, LCD_D6, LCD_D7);

unsigned long lastReadAt = 0;

void setup() {
  Serial.begin(SERIAL_BAUD_RATE);
  dht.begin();
  lcd.begin(16, 2);

  lcd.setCursor(0, 0);
  lcd.print("Tempest");
  lcd.setCursor(0, 1);
  lcd.print("Starting...");
  delay(1500);
  lcd.clear();
}

void loop() {
  unsigned long now = millis();

  if (now - lastReadAt < READ_INTERVAL_MS) {
    return;
  }

  lastReadAt = now;

  float humidity = dht.readHumidity();
  float temperatureC = dht.readTemperature();

  if (isnan(humidity) || isnan(temperatureC)) {
    Serial.println("status=error,error=sensor_read_failed");

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Sensor error");
    lcd.setCursor(0, 1);
    lcd.print("Check DHT11");
    return;
  }

  Serial.print("status=ok,temp_c=");
  Serial.print(temperatureC, 1);
  Serial.print(",humidity=");
  Serial.println(humidity, 1);

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Temp: ");
  lcd.print(temperatureC, 1);
  lcd.print(" C");

  lcd.setCursor(0, 1);
  lcd.print("Hum:  ");
  lcd.print(humidity, 1);
  lcd.print(" %");
}
