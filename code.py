import time
import board
from busio import I2C
import adafruit_is31fl3741
from adafruit_is31fl3741.adafruit_ledglasses import LED_Glasses
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.color_packet import ColorPacket

colorArr1 = []
colorArr2 = []
rgb_int1 = -1
rgb_int2 = -1
OFFSET = 0
BLACK = [0,0,0]
i2c = I2C(board.SCL, board.SDA, frequency=1000000)

def calculateIndex(value):
    value = value - 1
    return value

def calculateColor(value, color1, color2):
    if OFFSET == 0:
        ca = color1
        cb = color2
    else:
        ca = color2
        cb = color1

    if (value % 2):
        return ca
    else:
        return cb

# Initialize the IS31 LED driver, buffered for smoother animation
glasses = LED_Glasses(i2c, allocate=adafruit_is31fl3741.MUST_BUFFER)
glasses.show()  # Clear any residue on startup
glasses.global_current = 20  # Just middlin' bright, please

ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

while True:
    ble.start_advertising(advertisement)
    while not ble.connected:
        pass
    ble.stop_advertising()

    while True:
        if ble.connected:
            if uart.in_waiting:
                raw_bytes = uart.read(uart.in_waiting)
                try:
                    packet = Packet.from_bytes(raw_bytes)
                    if isinstance(packet, ColorPacket):
                        rgb_int = packet.color[0] << 16 | packet.color[1] << 8 | packet.color[2]
                        print ("RED: " + str(packet.color[0]))
                        print ("GREEN:" + str(packet.color[1]))
                        print ("BLUE: " + str(packet.color[2]))
                        print("RGB: " + str(rgb_int))
                        glasses.right_ring.fill(rgb_int)
                        glasses.left_ring.fill(rgb_int)
                        glasses.show()
                except ValueError:
                    text = raw_bytes.decode().strip()
                    print("RX:", text)
                    if (text.startswith("COLOR1=")):
                        print("COLOR FOUND")
                        colorsArr = text.replace("COLOR1=", "")
                        colorArr1 = colorsArr.split(",")
                        #print("COLOR: " + colorArr1)
                    elif (text.startswith("COLOR2=")):
                        print("COLOR FOUND")
                        colorsArr = text.replace("COLOR2=", "")
                        colorArr2 = colorsArr.split(",")
                        #print("COLOR: " + colorArr1)
                    elif (text.startswith("TEXT=")):
                        print("TEXT FOUND")
                    elif (text == "SHOW"):
                        rgb_int1 = int(colorArr1[0]) << 16 | int(colorArr1[1]) << 8 | int(colorArr1[2])
                        rgb_int2 = int(colorArr2[0]) << 16 | int(colorArr2[1]) << 8 | int(colorArr2[2])

                #uart.reset_input_buffer()

        if rgb_int1 > -1 and rgb_int2 > -1:
            for i in range(1,25):
                glasses.left_ring[calculateIndex(i)] = calculateColor(i, rgb_int1, rgb_int2)
                glasses.right_ring[calculateIndex(i)] = calculateColor(i, rgb_int1, rgb_int2)
            glasses.show()
            time.sleep(2)

        if OFFSET == 0:
            OFFSET = 1
        else:
            OFFSET = 0