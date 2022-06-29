from rpi_lcd import LCD

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import smbus
import pigpio
import time
import subprocess
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

lcd = LCD()

# Raspberry Pi pin configuration:
RST = 24

# 128x32 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Load default font.
font = ImageFont.load_default()

# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

i2c_ch = 1

lcd = LCD()

# TMP102 address on the I2C bus
i2c_address = 0x48

# Register addresses
reg_temp = 0x00
reg_config = 0x01

# Calculate the 2's complement of a number
def twos_comp(val, bits):
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val

# Read temperature registers and calculate Celsius
def read_temp():

    # Read temperature registers
    val = bus.read_i2c_block_data(i2c_address, reg_temp, 2)
    # NOTE: val[0] = MSB byte 1, val [1] = LSB byte 2
    #print ("!shifted val[0] = ", bin(val[0]), "val[1] = ", bin(val[1]))

    temp_c = (val[0] << 4) | (val[1] >> 4)
    #print (" shifted val[0] = ", bin(val[0] << 4), "val[1] = ", bin(val[1] >> 4))
    #print (bin(temp_c))

    # Convert to 2s complement (temperatures can be negative)
    temp_c = twos_comp(temp_c, 12)

    # Convert registers value to temperature (C)
    temp_c = temp_c * 0.0625 * 2.0253 

    return temp_c

# Initialize I2C (SMBus)
bus = smbus.SMBus(i2c_ch)

# Read the CONFIG register (2 bytes)
val = bus.read_i2c_block_data(i2c_address, reg_config, 2)
print("Old CONFIG:", val)

# Set to 4 Hz sampling (CR1, CR0 = 0b10)
val[1] = val[1] & 0b00111111
val[1] = val[1] | (0b10 << 6)

# Write 4 Hz sampling back to CONFIG
bus.write_i2c_block_data(i2c_address, reg_config, val)

# Read CONFIG to verify that we changed it
val = bus.read_i2c_block_data(i2c_address, reg_config, 2)
print("New CONFIG:", val)

# Print out temperature every second
try:
    while True:
        temperature = read_temp()
        fehrenheit = (temperature * 1.8) + 32
        print(round(temperature, 2), " C")
        temp_1 = (str(round(temperature,2))+" C")
        temp_2 = (str(round(fehrenheit,2))+" F")
        print(round(fehrenheit, 2), " F")
        lcd.text("Sensor TMP117", 1)
        lcd.text((temp_1+" "+ temp_2), 2)

        # print on graphic screen
        draw.text((x, top),        str(" Temp[%d]" % temperature), font=font, fill=255)
        draw.text((x, top+8),      str(temp_1),  font=font, fill=255)
        draw.text((x, top+16),     str(" Temp[%d]" % fehrenheit),  font=font, fill=255)
        draw.text((x, top+25),     str(temp_2),  font=font, fill=255)

        # Display image.
        disp.image(image)
        disp.display()

        time.sleep(3)

except KeyboardInterrupt:
    print("\nApplication stopped!")
    lcd.clear()
    disp.clear()
    disp.display()
