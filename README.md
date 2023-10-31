# RPIPico-Macroboard---Beginner-Project
**This is a simple macroboard made using Raspberry PI Pico and Circuitpython, with a couple of extra components to spice it up, such as:**
- A programmable ssd1306 oled screen for displaying custom wallpapers and command names
- Powerful default preset with support for various applications
- Simple and customizable code (made specifically to make adding new buttons/commands relatively simple)
- Knob control with a rotary encoder

## Setup
First and foremost, we are going to need:
- Raspberry Pi Pico (pico H and W should also work fine) with Circuitpython flashed onto it (I'm using version 8.2.6)
      *To flash it use the guide: https://learn.adafruit.com/getting-started-with-raspberry-pi-pico-circuitpython/circuitpython*
- Circuitpython library bundle on your Desktop, we will need some of the libraries in this for our project
- Simple Circuitry gear: breadboard, LEDs, jumper wires, pushbuttons (unless you want to jump straight from prototyping to a PCB)
- SSD1306 Oled 128x64 screen --Note: other models might also work, but this guide uses this screen specifically due to its low cost and good performance.
- Basic rotary encoder (works as long as it has the usual CLK, DT and SW pins, further explanations on them will come later)
- Mechanical keyboard switches

**Useful links:**
- https://learn.adafruit.com/scanning-i2c-addresses/circuitpython (I2C address finder)
- https://docs.circuitpython.org/projects/display_text/en/latest/api.html#adafruit_display_text.label.Label (documentation for the adafruit_display text libraries)
- https://docs.circuitpython.org/projects/displayio_ssd1306/en/latest/api.html#adafruit_displayio_ssd1306.SSD1306 (ssd1306 library documentation)
- https://circuitpython.org/libraries (download of all Circuitpython libraries, they can be found beneath the "lib" folder and need to be in the RPIs own lib folder)

## Installing and running code
Running the code should be as simple as plugging in your components, uploading in the correct pins to the program and using it, note, however, that the shortcuts are only a preset to build upon and should be changed if you want more shortcuts.
For this, take a look at the Keycode, Keyboard and Consumer Control libraries from adafruit for examples on how to add your own capabilities.

**Example:**
```
#add your shortcut to a button's corresponding actionIndex in the actionList in the specific mode you want it to be in:
#for example, here's how I would add Copy and Paste to the same button in different modes:

#define the shortcut in actionList
actionList = [[Keycode.COMMAND, Keycode.C], [Keycode.COMMAND, Keycode.V]]

#or on windows
actionList = [[Keycode.CONTROL, Keycode.C], [Keycode.CONTROL, Keycode.V]]

#define btn and actionIndex in index 0
button1 = btn(board.GP20, 0)
```
