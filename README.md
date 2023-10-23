# RPIPico-Macroboard---Beginner-Project
**This is a simple macroboard made using Raspberry PI Pico and Circuitpython, with a couple of extra components to spice it up, such as:**
- A programmable ssd1306 oled screen for displaying custom wallpapers and command names
- Support for RGB lighting (still to come)
- Simple and customizable code (made specifically to make adding new buttons/commands relatively simple)

#Setup
First and foremost, we are going to need:
- Raspberry Pi Pico (pico H and W should also work fine) with Circuitpython flashed onto it (I'm using version 8.2.6)
- Simple Circuitry gear: breadboard, LEDs, jumper wires, pushbuttons (unless you want to jump straight from prototyping to a PCB)
- SSD1306 Oled 128x64 screen --Note: other models might also work, but this guide uses this screen specifically due to its low cost and good performance.

**Useful links:**
- https://learn.adafruit.com/scanning-i2c-addresses/circuitpython (I2C address finder)
- https://docs.circuitpython.org/projects/display_text/en/latest/api.html#adafruit_display_text.label.Label (documentation for the adafruit_display text libraries)
- https://docs.circuitpython.org/projects/displayio_ssd1306/en/latest/api.html#adafruit_displayio_ssd1306.SSD1306 (ssd1306 library documentation)
- https://circuitpython.org/libraries (download of all Circuitpython libraries, they can be found beneath the "lib" folder and need to be in the RPIs own lib folder)
