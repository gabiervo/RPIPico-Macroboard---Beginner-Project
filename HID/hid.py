import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
import adafruit_hid.consumer_control
from adafruit_hid.consumer_control_code import ConsumerControlCode
import displayio, busio, adafruit_displayio_ssd1306, terminalio
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
from displayio import Bitmap
import time
import asyncio
import analogio
import math, rotaryio

#define the consumer_control object, the library does not work without it
consumer_control = ConsumerControl(usb_hid.devices)

keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)

displayio.release_displays()

#setting the pins which will be used for the communication between the board and the screen
sda, scl = board.GP0, board.GP1

#sets up the protocol the screen uses for communication with the board
#for more info on i2c check: https://www.circuitbasics.com/basics-of-the-i2c-communication-protocol/
i2c = busio.I2C(scl, sda)
#i2c device addresses can be found using the link: https://learn.adafruit.com/scanning-i2c-addresses/circuitpython
#just make sure you have your i2c pins hooked up to the board before running the program
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)

#make the display context
#displayio.Group essentially sets a blank canvas for us to draw on, while display.show transfers that onto the screen
splash = displayio.Group()
display.show(splash)

#set default settings
#Bitmap takes in the width and height of the display, as well as the bits per pixel, since we only need black and white
#in this case, we put one bit per pixel, meaning black or white
color_bitmap = displayio.Bitmap(128, 64, 1)
color_palette = displayio.Palette(2)
color_palette[0] = 0x000000  # Black
color_palette[1] = 0xFFFFFF  # White

#label color customization: textBG makes the background either black or white and textColor makes the text either black or white
textBG = 0 
textColor = 1
mineFont = bitmap_font.load_font("Minecraftia-Regular-75.bdf", Bitmap)

# sets the list of background images, you can put in the directories for any of your own bmp images here
bgList = ["sky.bmp"]
bgIndex = 0

#determines which "mode" the user is in, remember that each mode has a set of shortcuts you can set for it
funcVal = 0

#sets the shortcuts for each mode:
#    main list -> holds all the other lists
#    \
#     | Mode lists -> hold the shortcuts for each mode
#      \
#       | Shortcut lists -> hold a list of commands that are run as shortcuts according to their indexes
actionList = [[[Keycode.SHIFT, Keycode.B], [Keycode.SHIFT, Keycode.C], [Keycode.OPTION, Keycode.CONTROL, Keycode.RIGHT_ARROW]],[[Keycode.COMMAND, Keycode.C], [Keycode.COMMAND, Keycode.V], [Keycode.OPTION, Keycode.CONTROL, Keycode.LEFT_ARROW]]]

#optional led made to check if your board is recognizing button inputs without the use of the Serial Monitor
led = digitalio.DigitalInOut(board.GP16)
led.direction = digitalio.Direction.OUTPUT
led.value = False

#rotary encoder clk = a | dt = b
encoder = rotaryio.IncrementalEncoder(board.GP21, board.GP22)

#rotary encoder button
sw = digitalio.DigitalInOut(board.GP15)
sw.direction = digitalio.Direction.INPUT
sw.pull = digitalio.Pull.UP
currVol = 8
frame = 0

def loadStartScreen(isDefault):
    #sets a new display "canvas"
    splash = displayio.Group()
    try:
        #opens either a normal bg image or an animation frame, being setup for an animation feature I'm still working on
        if isDefault == True:
            imgFile = open(bgList[bgIndex], "rb")
        else:
            imgFile = open("/animation/" + str(frame) + ".bmp", "rb")
            
        #the code then saves that bitmap and some text on disk, before displaying it on the screen
        bgImg = displayio.OnDiskBitmap(imgFile)
        bgImgArea = displayio.TileGrid(bgImg, pixel_shader=color_palette)
        text_area = label.Label(terminalio.FONT, text="Mode: " + str(funcVal), color=color_palette[textColor], padding_top=2, padding_bottom=10, padding_left=4, padding_right=100, background_color=color_palette[textBG], x=3, y=57)

        splash.append(bgImgArea)
        splash.append(text_area)
        display.refresh()
        display.show(splash)
    except MemoryError: 
        #if the board runs into an error it just blanks out and recurses onto the function to try and load the background again
        splash = displayio.Group()
        display.show(splash)
        loadStartScreen(True)
    
#refreshes the display for animation, background and button press related text
def refreshDisplay(dispIn, functions):
    if dispIn == "animate":
        loadStartScreen(False)
    if dispIn == "default":
        loadStartScreen(True)
    else:
        splash = displayio.Group()
        display.show(splash)
        dispIn = dispIn + "\n" + functions
        text_area = label.Label(terminalio.FONT, text=dispIn, color=0xFFFF00, x=28, y=28)
        splash.append(text_area)
        display.refresh()
    
shouldAnimate = False

async def resetDisplay():
    if shouldAnimate == True:
        refreshDisplay("animate", "none")
    else:
        refreshDisplay("default", "none")

refreshDisplay("default", "none")

shouldHaveBtnScreen = False
class btn:
    #creates the button class, responsible for more easily being able to define buttons and pins
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
        led.value = False
        while self.button.value is not True:
            pass

# you can define the buttons with: buttonName = btn(board.btnPin, actionIndex, ["function1", "function2"]
btn1 = btn(board.GP17, 0, ["Type B", "Copy"])
btn2 = btn(board.GP18, 1, ["Type C", "Paste"])
btn3 = btn(board.GP19, 2, ["Right Half", "Left Half"])
funcButton = btn(board.GP20, -1, ["funcbtn", "funcbtn"])

last_pos = -10000

#reset sound:
for i in range(16):
    consumer_control.send(ConsumerControlCode.VOLUME_DECREMENT)
for i in range(8):
    consumer_control.send(ConsumerControlCode.VOLUME_INCREMENT)

#this variable is supposed to tell the program whether or not to reset the display at the end of a cycle if it is animating
#essentially, whenever anything uses the screen, it resets the display at some point, however, if nothing has reset the screen this 
#cycle we still want the animation running, so this variable exists for just that
hasSomethingOccurred = False
while True:
    curr_pos = encoder.position
    if last_pos == -10000 or last_pos != curr_pos:
        if int(last_pos) > int(curr_pos):
            consumer_control.send(ConsumerControlCode.VOLUME_DECREMENT)
            currVol -= 1
        if int(last_pos) < int(curr_pos):
            consumer_control.send(ConsumerControlCode.VOLUME_INCREMENT)
            currVol += 1
        if currVol < 0:
            currVol = 0
        if currVol > 16:
            currVol = 16
        print(curr_pos)
        hasSomethingOccurred = True
    last_pos = curr_pos

    #checking all button presses and functions, I'm thinking of changing this into something built into the class of btn
    if sw.value is not True:
        hasSomethingOccurred = True
        print("pressed sw")
        for i in range(16):
            consumer_control.send(ConsumerControlCode.VOLUME_DECREMENT)
        currVol = 0
    
    if btn1.button.value is not True:
        hasSomethingOccurred = True
        btn1.pressButtons()
        if shouldHaveBtnScreen == True:
            refreshDisplay("btn1 pressed", btn1.functions[funcVal])
            asyncio.run(resetDisplay())
        
    if btn2.button.value is not True:
        hasSomethingOccurred = True
        btn2.pressButtons()
        if shouldHaveBtnScreen == True:
            refreshDisplay("btn2 pressed", btn2.functions[funcVal])
            asyncio.run(resetDisplay())
    
    if btn3.button.value is not True:
        hasSomethingOccurred = True
        btn3.pressButtons()
        if shouldHaveBtnScreen == True:
            refreshDisplay("btn3 pressed", btn3.functions[funcVal])
            asyncio.run(resetDisplay())

    #funcButton is a lot longer because it possesses a lot of unique functions of its own, and also allows for the use of shortcuts for some settings
    if funcButton.button.value is not True:
        hasSomethingOccurred = True
        funcVal += 1
        if funcVal >= 2:
            funcVal = 0
        print(funcVal)
        asyncio.run(resetDisplay())
        while funcButton.button.value is not True:
            if btn3.button.value is not True:
                bgIndex += 1
                if bgIndex > len(bgList)-1:
                    bgIndex = 0
                asyncio.run(resetDisplay())
                time.sleep(0.1)
            if btn2.button.value is not True:
                if textBG == 0:
                    textBG = 1
                    textColor = 0
                else:
                    textBG = 0
                    textColor = 1
                asyncio.run(resetDisplay())
                time.sleep(0.1)
    if hasSomethingOccurred == False and shouldAnimate == True:
        asyncio.run(resetDisplay)
