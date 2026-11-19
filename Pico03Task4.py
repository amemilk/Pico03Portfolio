from machine import Pin, I2C, UART
import time

UART_OBSTACLE = UART(0, baudrate = 9600, rx=Pin(13))
UART_SOUND = UART(1, baudrate = 9600, rx=Pin(9))

RGB_PINS = (12, 10, 8)




i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)

# Logic 1: scan the I2C bus
devices = i2c.scan()
print("I2C devices found:", [hex(d) for d in devices])
ADDR = devices[0]

# Small helper functions to talk to the LCD backpack
BACKLIGHT = 0x08
ENABLE = 0x04

def write4(bits):
    i2c.writeto(ADDR, bytes([bits | BACKLIGHT | ENABLE]))
    time.sleep_us(1)
    i2c.writeto(ADDR, bytes([bits | BACKLIGHT]))
    time.sleep_us(50)

def send(byte, mode):
    write4((byte & 0xF0) | mode)
    write4(((byte << 4) & 0xF0) | mode)

def command(c):
    send(c, 0)
    time.sleep_ms(2)

def lcd_start():
    time.sleep_ms(50)
    for i in range(3):
        write4(0x30)
        time.sleep_ms(5)
    write4(0x20)        # 4-bit mode
    command(0x28)       # 2 rows, 5x8 dots
    command(0x0C)       # display on, cursor off
    command(0x06)       # move right after each character
    command(0x01)       # clear the screen

def lcd_print(text, row):
    if row == 1:
        command(0x80)   # start of row 1
    else:
        command(0xC0)   # start of row 2
    for ch in text[:16]:
        send(ord(ch), 1)


lcd_start()
while True:
    # Check for messages from Board 2
    if UART_OBSTACLE.any():
        raw_OBSTACLE = UART_OBSTACLE.readline()
        if raw_OBSTACLE:
            decoded = raw_OBSTACLE.decode('utf-8').strip()
            lcd_print("                ",1)
            lcd_print(decoded,1)
            

    # Check for messages from Board 3
    if UART_SOUND.any():
        raw_SOUND = UART_SOUND.readline()
        if raw_SOUND:
            decoded2 = raw_SOUND.decode('utf-8').strip()
            lcd_print("                ",2)
            lcd_print(decoded2,2)

    time.sleep(0.1)