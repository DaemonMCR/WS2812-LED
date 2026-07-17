#include <Adafruit_NeoPixel.h>
#include <EEPROM.h>
#include "WS2812_Definitions.h"

#define PIN 4 // The digital PWM used
#define LED_COUNT 5 // Number of WS2812 LEDs wired up
#define SERIAL 115200 // Serial baud
#define VERSION "v1.0.0" // Software version

int currentIntensity = 100;

Adafruit_NeoPixel leds = Adafruit_NeoPixel(LED_COUNT, PIN, NEO_RGB + NEO_KHZ800);

void setup()
{
  // Start serial connection
  Serial.begin(SERIAL);

  // Initialise LEDs
  leds.begin();
  clearLEDs();
  leds.show();

  // Used via random()
  randomSeed(analogRead(0));
}

void loop()
{
  // Ensure serial connection is available
  if (Serial.available())
  {
    // Process data over serial
    String line = Serial.readStringUntil('\n');
    line.trim();

    int led_num, led_start, led_end, intensity, r, g, b;

    if (line == "HELP") {
      Serial.println("Available commands:");
      Serial.println("");
      Serial.println("HELP - usage: HELP");
      Serial.println("SET - usage: SET {LED_NUMBER} {RED_VALUE} {GREEN_VALUE} {BLUE_VALUE}");
      Serial.println("SET_RANGE - usage: SET_RANGE {START_LED}-{END_LED} {RED_VALUE} {GREEN_VALUE} {BLUE_VALUE}");
      Serial.println("GET - usage: GET {LED_NUMBER}");
      Serial.println("CLEAR - usage: CLEAR {LED_NUMBER}");
      Serial.println("CLEAR_ALL - usage: CLEAR_ALL");
      Serial.println("FILL - usage: FILL {RED_VALUE} {GREEN_VALUE} {BLUE_VALUE}");
      Serial.println("INTENSITY - usage: INTENSITY {INTENSITY_PERCENTAGE}");
      Serial.println("GET_INTENSITY - usage: GET_INTENSITY");
      Serial.println("RANDOM - usage: RANDOM");
      Serial.println("SAVE - usage: SAVE");
      Serial.println("LOAD - usage: LOAD");
      Serial.println("VERSION - usage: VERSION");
    }
    else if (sscanf(line.c_str(), "SET %d %d %d %d", &led_num, &r, &g, &b) == 4) {
      if (led_num >= 0 && led_num < LED_COUNT) {
        leds.setPixelColor(led_num, leds.Color(r, g, b));
        leds.show();
      }
      Serial.print("Set LED ");
      Serial.print(led_num);
      Serial.print(" to ");
      Serial.print(r);
      Serial.print(" ");
      Serial.print(g);
      Serial.print(" ");
      Serial.println(b);
    }
    else if (sscanf(line.c_str(), "SET_RANGE %d-%d %d %d %d", &led_start, &led_end, &r, &g, &b) == 5) {
      if (led_start <= led_end) {
        for (int i=led_start; i<=led_end; i++)
        {
          leds.setPixelColor(i, leds.Color(r, g, b));
        }
        leds.show();
      }
      else if (led_start > led_end) {
        for (int i=led_end; i<=led_start; i++)
        {
          leds.setPixelColor(i, leds.Color(r, g, b));
        }
        leds.show();
      }
      Serial.print("Set LED ");
      Serial.print(led_start);
      Serial.print("-");
      Serial.print(led_end);
      Serial.print(" to ");
      Serial.print(r);
      Serial.print(" ");
      Serial.print(g);
      Serial.print(" ");
      Serial.println(b);
    }
    else if (sscanf(line.c_str(), "GET %d", &led_num) == 1) {
      if (led_num >= 0 && led_num < LED_COUNT) {
        uint32_t color = leds.getPixelColor(led_num);

        r = (color >> 16) & 0xFF;
        g = (color >> 8) & 0xFF;
        b = color & 0xFF;

        Serial.print("LED ");
        Serial.print(led_num);
        Serial.print(": R=");
        Serial.print(r);
        Serial.print(" G=");
        Serial.print(g);
        Serial.print(" B=");
        Serial.println(b);
      }
    }
    else if (sscanf(line.c_str(), "CLEAR %d", &led_num) == 1) {
      leds.setPixelColor(led_num, 0x000000);
      leds.show();
      Serial.print("Cleared LED ");
      Serial.println(led_num);
    }
    else if (line == "CLEAR_ALL") {
      for (int i=0; i<LED_COUNT; i++)
      {
        leds.setPixelColor(i, 0x000000);
      }
      leds.show();
      Serial.println("Cleared all LEDs");
    }
    else if (sscanf(line.c_str(), "FILL %d %d %d", &r, &g, &b) == 3) {
      for (int i=0; i<LED_COUNT; i++)
      {
        leds.setPixelColor(i, leds.Color(r, g, b));
      }
      leds.show();
      Serial.print("Set all LEDs to ");
      Serial.print(r);
      Serial.print(" ");
      Serial.print(g);
      Serial.print(" ");
      Serial.println(b);
    }
    else if (sscanf(line.c_str(), "INTENSITY %d", &intensity) == 1) {
      intensity = constrain(intensity, 0, 100);

      currentIntensity = intensity;

      // Convert 0-100% to 0-255
      leds.setBrightness((intensity * 255) / 100);
      leds.show();

      Serial.print("Set intensity of all LEDs to ");
      Serial.print(intensity);
      Serial.println("%");
    }
    else if (line == "GET_INTENSITY") {
      Serial.print("Current intensity: ");
      Serial.print(currentIntensity);
      Serial.println("%");
    }
    else if (line == "RANDOM") {
      for (int i=0; i < 200; i++) {
        for (int i=0; i<LED_COUNT; i++)
        {
          leds.setPixelColor(i, leds.Color(random(0,255), random(0,255), random(0,255)));
        }
        leds.show();
        delay(75);
      }
      for (int i=0; i<LED_COUNT; i++)
      {
        leds.setPixelColor(i, 0x000000);
      }
      leds.show();
    }
    else if (line == "SAVE") {
      saveLEDs();
      Serial.println("Saved current RGB values of all LEDs");
    }
    else if (line == "LOAD") {
      loadLEDs();
      Serial.println("Loaded RGB values from previous save");
    }
    else if (line == "VERSION") {
      Serial.println(VERSION);
    }
    else {
      Serial.println("Invalid cmd!");
    }
  }
}

void saveLEDs()
{
  int address = 0;

  for (int i = 0; i < LED_COUNT; i++)
  {
    uint32_t colour = leds.getPixelColor(i);

    byte r = (colour >> 16) & 0xFF;
    byte g = (colour >> 8) & 0xFF;
    byte b = colour & 0xFF;

    EEPROM.update(address++, r);
    EEPROM.update(address++, g);
    EEPROM.update(address++, b);
  }
}

void loadLEDs()
{
  int address = 0;

  for (int i = 0; i < LED_COUNT; i++)
  {
    byte r = EEPROM.read(address++);
    byte g = EEPROM.read(address++);
    byte b = EEPROM.read(address++);

    leds.setPixelColor(i, leds.Color(r, g, b));
  }

  leds.show();
}

void clearLEDs()
{
  for (int i=0; i<LED_COUNT; i++)
  {
    leds.setPixelColor(i, 0);
  }
}
