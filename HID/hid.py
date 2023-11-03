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
import math, rotaryio, re

#we have to define this ConsumerControl object because, for some reason, when we call any of the methods within the
#consumer control class without defining it as an object, the "self" is never resolved, resulting in an error
#usb_hid.devices is nothing more than our computer, and thus, by creating a proper object with proper arguments
#we are able to use consumer control just fine, note that the examples on the adafruit website are, frankly, bad,
#since they don't take into account a scenario where your device is not immediately detected and/or it can't resolve
#the class.
consumer_control = ConsumerControl(usb_hid.devices)

keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)

displayio.release_displays()

sda, scl = board.GP0, board.GP1

i2c = busio.I2C(scl, sda)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)

#make the display context
splash = displayio.Group()
display.show(splash)

#set default settings
color_bitmap = displayio.Bitmap(128, 64, 1)
color_palette = displayio.Palette(2)
color_palette[0] = 0x000000  # Black
color_palette[1] = 0xFFFFFF  # White

#label color customization

with open("settings.txt", "r") as settings:
    setList = settings.readlines()
    setList.pop(0)
    print(setList)
    for i in range(len(setList)):
        listStr = setList[i]
        finalStr = ""
        for x in listStr:
            if x.isdigit() == True:
                finalStr = finalStr + x
        setList[i] = finalStr
    print(setList)
    bgIndex = int(setList[0])
    textColor = int(setList[1])
    funcVal = int(setList[2])
mineFont = bitmap_font.load_font("Minecraftia-Regular-75.bdf", Bitmap)

# Draw a label
bgList = ["sky.bmp", "moon.bmp", "cubes.bmp", "triforce.bmp", "planets.bmp"]

actionList = [[[Keycode.SHIFT, Keycode.B], [Keycode.SHIFT, Keycode.C], [Keycode.OPTION, Keycode.CONTROL, Keycode.RIGHT_ARROW]],[[Keycode.COMMAND, Keycode.C], [Keycode.COMMAND, Keycode.V], [Keycode.OPTION, Keycode.CONTROL, Keycode.LEFT_ARROW]]]
funcNameList = ["testMode", "copyMode"]
led = digitalio.DigitalInOut(board.GP16)
led.direction = digitalio.Direction.OUTPUT
led.value = False

#rotary encoder clk = a | dt = b
encoder = rotaryio.IncrementalEncoder(board.GP21, board.GP22)

sw = digitalio.DigitalInOut(board.GP15)
sw.direction = digitalio.Direction.INPUT
sw.pull = digitalio.Pull.UP
currVol = 8

def loadStartScreen(isDefault):
    splash = displayio.Group()
    try:
        try:
            imgFile = open(bgList[bgIndex], "rb")
        except IndexError:
            imgFile = open(bgList[0], "rb")
        bgImg = displayio.OnDiskBitmap(imgFile)
        bgImgArea = displayio.TileGrid(bgImg, pixel_shader=color_palette)
        text_area = label.Label(terminalio.FONT, text="Mode: " + str(funcVal), color=color_palette[textColor], padding_top=2, padding_bottom=10, padding_left=4, padding_right=100, background_color=color_palette[not textColor], label_direction="LTR", x=3, y=57)
        funcName = label.Label(terminalio.FONT, text=funcNameList[funcVal], color=color_palette[textColor], label_direction="LTR", x=80, y=57)

        splash.append(bgImgArea)
        splash.append(text_area)
        splash.append(funcName)
        display.refresh()
        display.show(splash)
    except MemoryError: 
        splash = displayio.Group()
        display.show(splash)
    

def refreshDisplay(dispIn, functions):
    if dispIn == "default":
        loadStartScreen(True)
    else:
        splash = displayio.Group()
        display.show(splash)
        dispIn = dispIn + "\n" + functions
        text_area = label.Label(terminalio.FONT, text=dispIn, color=0xFFFF00, x=28, y=28)
        splash.append(text_area)
        display.refresh()
    
async def resetDisplay():
    refreshDisplay("default", "none")

refreshDisplay("default", "none")

shouldHaveBtnScreen = False
class btn:
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

while True:
    curr_pos = encoder.position
    if last_pos == -10000 or last_pos != curr_pos:
        if int(last_pos) > int(curr_pos):
            consumer_control.send(ConsumerControlCode.VOLUME_DECREMENT)
        if int(last_pos) < int(curr_pos):
            consumer_control.send(ConsumerControlCode.VOLUME_INCREMENT)
        print(curr_pos)
    last_pos = curr_pos
    
    if sw.value is not True:
        print("pressed sw")
        for i in range(16):
            consumer_control.send(ConsumerControlCode.VOLUME_DECREMENT)
    
    if btn1.button.value is not True:
        btn1.pressButtons()
        if shouldHaveBtnScreen == True:
            refreshDisplay("btn1 pressed", btn1.functions[funcVal])
            asyncio.run(resetDisplay())
        
    if btn2.button.value is not True:
        btn2.pressButtons()
        if shouldHaveBtnScreen == True:
            refreshDisplay("btn2 pressed", btn2.functions[funcVal])
            asyncio.run(resetDisplay())
    
    if btn3.button.value is not True:
        btn3.pressButtons()
        if shouldHaveBtnScreen == True:
            refreshDisplay("btn3 pressed", btn3.functions[funcVal])
            asyncio.run(resetDisplay())
    if funcButton.button.value is not True:
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
                if textColor == 0:
                    textColor = 1
                else:
                    textColor = 0
                asyncio.run(resetDisplay())
                time.sleep(0.1)
