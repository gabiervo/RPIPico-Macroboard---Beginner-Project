# RPIPico-Macroboard---Beginner-Project
**This is a simple macroboard made using Raspberry PI Pico and Circuitpython, with a couple of extra components to spice it up, such as:**
- A programmable ssd1306 oled screen for displaying custom wallpapers and command names
- Support for RGB lighting (still to come)
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

## Getting started (prototyping)
*Note: this step is completely optional, if you want to jump straight into the final PCB, jump to the Finishing Up section of the project.*

First, plug in the RPI into your desktop with a **data and power USB cable**, if you installed and setup the Pi correctly, it should show up as a CIRCUITPY drive, in it there should be a couple of files, the ones that interest us the most, however are *code.py and lib*, code.py will be where the code we run will be stored, and lib will store all of our libraries  and directories. 
*For more info: https://learn.adafruit.com/welcome-to-circuitpython/the-circuitpy-drive*

Now, connect, to a breadboard:
- 4 pushbuttons
- One rotary encoder
- One SSD1306 oled screen
- One LED
  
Remember to use the correct pins for output (the SCL and SDA pins should use pins that are capable of communicating through an I2C interface, so be mindful of that, to check, use the image below: https://www.14core.com/wp-content/uploads/2022/11/Raspberry-Pi-PICO-Pinout-Diagram.jpeg

Finally, to check that everything is working, use the *test.py* file, you need to change the pins in the file to resemble your own, so make sure to read through it to understand the basic functionality of CIRCUITPYTHON, though we will cover this in more detail later on when we do an overview of the final program.

**This program should make it so that, whenever you press a button or change the position of the rotary encoder, something appears either in the console or in the OLED screen**
