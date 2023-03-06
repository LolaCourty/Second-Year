import time
import helpers

from robust_serial import write_order, Order, write_i8, read_i16, read_i8, read_i32
from robust_serial.threads import CommandThread, ListenerThread
from robust_serial.utils import open_serial_port

BAUDRATE = 115200

serial_file = open_serial_port(baudrate=BAUDRATE)
# Perform handshake with Arduino:
is_connected = False
while not is_connected:
    write_order(serial_file, Order.HELLO)
    bytes_array = bytearray(serial_file.read(1))
    print(bytes_array)
    if not bytes_array:
        time.sleep(2)
        continue
    byte = bytes_array[0]
    if byte in [Order.HELLO.value, Order.ALREADY_CONNECTED.value]:
        is_connected = True

print("Connected to the serial thing")

### ABSOLUTELY NEEDED TO MAKE THE THINGS WORK
time.sleep(1)
serial_file.flushInput()
###

while True:
    print(helpers.read_sonic(serial_file))
    #print(helpers.read_sharp(serial_file))
    time.sleep(0.5)
