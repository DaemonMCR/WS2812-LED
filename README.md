# WS2812-LED Project for TLS

This software was designed to run on the Elegoo Uno R3 board in combination with WS2812 LEDs. The backend code was written with arduino and can be found in the WS2812_main subdirectory and the frontend was written via the help of a ChatGPT model in python.

# Executing
The software can either be run with TLS via the recipe file - WS2812_TLS.rcp - or directly through the python file - main.py. From there a command can be entered into the "Serial Command" box and then executed.

# Things to note
Currently the software has the digital PWM and number of LEDs hardcoded. To change the Digital (PWM ~) used, change the "PIN" macro in the arduino code. To change the number of LEDs hooked up to the board change the "LED_COUNT" macro.

# Usage
- HELP - usage: HELP
- SET - usage: SET {LED_NUMBER} {RED_VALUE} {GREEN_VALUE} {BLUE_VALUE}
- SET_RANGE - usage: SET_RANGE {START_LED}-{END_LED} {RED_VALUE} {GREEN_VALUE} {BLUE_VALUE}
- GET - usage: GET {LED_NUMBER}
- CLEAR - usage: CLEAR {LED_NUMBER}
- CLEAR_ALL - usage: CLEAR_ALL
- FILL - usage: FILL {RED_VALUE} {GREEN_VALUE} {BLUE_VALUE}
- INTENSITY - usage: INTENSITY {INTENSITY_PERCENTAGE}
- RANDOM - usage: RANDOM
- SAVE - usage: SAVE
- LOAD - usage: LOAD
- VERSION - usage: VERSION

# Library used
Adafruit Neopixel - https://github.com/adafruit/adafruit_neopixel