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

i2c = I2C(board.SCL, board.SDA, frequency=1000000)

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

        while ble.connected:
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
                    if (text.startswith("COLOR=")):
                        print("COLOR FOUND")
                        colorArr = text.replace("COLOR=", "").split(",")
                        print ("RED: " + str(colorArr[1]))
                        print ("GREEN: " + str(colorArr[2]))
                        print ("BLUE: " + str(colorArr[3]))
                        rgb_int = int(colorArr[1]) << 16 | int(colorArr[2]) << 8 | int(colorArr[3])

                        if (int(colorArr[0]) == 1):
                            print("COLOR 1")
                            glasses.left_ring.fill(rgb_int)
                        else:
                            print("COLOR 2")
                            glasses.right_ring.fill(rgb_int)
                    elif (text.startswith("TEXT=")):
                        print("TEXT FOUND")
                    elif (text == "SHOW"):
                        glasses.show()