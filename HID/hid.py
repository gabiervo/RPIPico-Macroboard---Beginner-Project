#import circuitpython and python libraries
import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
import displayio, busio, adafruit_displayio_ssd1306, terminalio
from adafruit_display_text import label
import time
import asyncio

#defining your keyboard using the usb_hid library (the variable keyboard is going to be the one we use for most interaction with the actual computer)
keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)

#defining the i2c display
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64

displayio.release_displays()

#most of this is boilerplate code to get the OLED display setup and ready for use
#remember, however that you will need to change a couple of things here, let's run through them:

# the sda and scl pins are responsible for communication between the screen and the board, thus, you need to have
# them wired correctly (note, these are not the only sda and scl pins on a pico, but they are the simplest to remember)
sda, scl = board.GP0, board.GP1

i2c = busio.I2C(scl, sda)

# here, you will more likely than not have to use a different device_address, if your vendor does not inform you of your board's device address
# use the following adafruit link to find it: https://learn.adafruit.com/scanning-i2c-addresses/circuitpython
# if, even with the program, no i2c addresses show up, try to reverse the position of your scl and sda pins above (I myself wired them wrong the first time)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)

#make the display context (this essentially just clears out the screen)
splash = displayio.Group()
display.show(splash)

#set default settings (this sets stuff like the size of the display and the color pallette, since we have a monochrome screen we use black and white)
color_bitmap = displayio.Bitmap(128, 64, 1)
color_palette = displayio.Palette(2)
color_palette[0] = 0x000000  # White
color_palette[1] = 0xFFFFFF  # White

# Draw the background
# Has to be a 128x50 monochrome bmp file 

# First get an image file you like, preferably small pixel art, and crop it to fit the 128x50 size,
# then, using the image converter program located in the project files, convert your image to bmp and clean up any faulty conversion artifacts

#the sky.bmp file will be located within the project directory, the name can be changed to the file of your choice 
imgFile = open("sky.bmp", "rb")
bgImg = displayio.OnDiskBitmap(imgFile)

#displays the selected image and mode on the screen on boot (mode will be covered in the next couple of lines)
bgImgArea = displayio.TileGrid(bgImg, pixel_shader=color_palette)
text_area = label.Label(terminalio.FONT, text="Mode: 0", color=0xFFFF00, x=0, y=60)

#remember when we set the display context? There, we set a sort of canvas for the screen, now we are simply appending our images to it
splash.append(bgImgArea)
splash.append(text_area)
display.refresh()

# the list below provides all the  macros already written onto the board (placeholders)
# The list itself is a matrix upon a matrix kind of:
# basically, the larger list holds the overall content of possible actions 
# the smaller lists within those hold the commands for each mode (essentially so that we can store as many macros as we want, since you can always change the mode you are using)
# the smallest of lists hold the macros themselves, each macro can have up to six individual commands, every macro has to be a list with up to 6 commands (according to adafruit documentation) placed in order, to write new commands follow the model below:
#
#           Keycode.KEY (full uppercase)
#

actionList = [[[Keycode.SHIFT, Keycode.B], [Keycode.SHIFT, Keycode.C], [Keycode.OPTION, Keycode.CONTROL, Keycode.RIGHT_ARROW]],[[Keycode.COMMAND, Keycode.C], [Keycode.COMMAND, Keycode.V], [Keycode.OPTION, Keycode.CONTROL, Keycode.LEFT_ARROW]]]

#remember, the wiring for the buttons and leds are completely arbitrary, just try to avoid placing them in pins that allow analog communication (26, 27)
# just more boilerplate though, DigitalInOut defines the placing within the board, Direction is INPUT/OUTPUT, pull should be UP for the buttons
led = digitalio.DigitalInOut(board.GP16)
led.direction = digitalio.Direction.OUTPUT
led.value = False

#funcVal determines the "mode" you're currently in, modes, recalling, determine the list of macros available to you
funcVal = 0
class btn:
    #instead of defining each button manually, which would be a nightmare, I coded a function to do most of the functions of the button for you, actionIndex defines what action the button should do in the context of actionList, functions defines the name of the actions the button can do (should be made as a list with strings for the button's functions)
    def __init__(self, pin, actionIndex, functions):
        self.pin = pin
        self.button = digitalio.DigitalInOut(pin)
        self.button.direction = digitalio.Direction.INPUT
        self.button.pull = digitalio.Pull.UP
        self.actionIndex = actionIndex
        self.functions = functions
    
    def pressButtons(self):
        led.value = True
        for i in actionList[funcVal][self.actionIndex]:
            keyboard.press(i)
            print(i)
        keyboard.release_all()
        time.sleep(0.15)
        led.value = False

#normal buttons
btn1 = btn(board.GP17, 0, ["Type B", "Copy"])
btn2 = btn(board.GP18, 1, ["Type C", "Paste"])
btn3 = btn(board.GP19, 2, ["Right Half", "Left Half"])

#the funcButton, changes the mode you are using
funcButton = btn(board.GP20, -1, ["funcbtn", "funcbtn"])

#the function below is the function that is used to flash images to the display depending on what you do
def refreshDisplay(dispIn, functions):
    #resets the display
    splash = displayio.Group()
    display.show(splash)
    display.refresh()

    #occurs if the user wants to return to the background of his/her choice
    if dispIn == "default":
        #places background
        imgFile = open("sky.bmp", "rb")
        bgImg = displayio.OnDiskBitmap(imgFile)
        bgImgArea = displayio.TileGrid(bgImg, pixel_shader=color_palette)

        #places text
        text_area = label.Label(terminalio.FONT, text="Mode: " + str(funcVal), color=0xFFFF00, x=0, y=60)

        splash.append(bgImgArea)
        splash.append(text_area)
        display.refresh()
    else:
        # in any other case, we simply display what button you pressed + it's function using a text label
        dispIn = dispIn + "\n" + functions
        text_area = label.Label(terminalio.FONT, text=dispIn, color=0xFFFF00, x=28, y=28)
        splash.append(text_area)
        display.refresh()
    
async def resetDisplay():
    #code for, whenever the screen changes due to pressing a button, it returns to the base background
    await asyncio.sleep(0.1)
    refreshDisplay("default", "none")
       
while True:
    if btn1.button.value is not True:
        #the template for every press button event, first we call the pressButtons function which executes the keycode commands properly
        #then we refresh the display with the text in the first argument, followed by the text in the second argument in the line below, before finally returning the display to its IDLE state
        btn1.pressButtons()
        refreshDisplay("btn1 pressed", btn1.functions[funcVal])
        asyncio.run(resetDisplay())
        
    if btn2.button.value is not True:
        refreshDisplay("btn2 pressed", btn2.functions[funcVal])
        btn2.pressButtons()
        asyncio.run(resetDisplay())
    
    if btn3.button.value is not True:
        refreshDisplay("btn3 pressed", btn3.functions[funcVal])
        btn3.pressButtons()
        asyncio.run(resetDisplay())
    
    if funcButton.button.value is not True:
        #special event specifically if we want to change the function mode
        funcVal += 1
        if funcVal >= 2:
            funcVal = 0
        print(funcVal)
        asyncio.run(resetDisplay())

