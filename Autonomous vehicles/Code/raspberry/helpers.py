import struct
from robust_serial import write_order, Order, write_i8, read_i32, read_i16, read_i8
import time

def move(serial_file, speed=100, ratio=0):
    if speed == 0:
        write_order(serial_file, Order.STOP)
    else:
        write_order(serial_file, Order.MOTOR)
        aratio = abs(ratio)
        if ratio > 0:
            write_i8(serial_file, int(speed))
            write_i8(serial_file, int(speed*(1-aratio)))
        else:
            write_i8(serial_file, int(speed*(1-aratio)))
            write_i8(serial_file, int(speed))
    return "OK Move"


def rotate(serial_file, speed):
    if speed:
        write_order(serial_file, Order.MOTOR)
        write_i8(serial_file, -int(speed))
        write_i8(serial_file, int(speed))
    else:
        write_order(serial_file, Order.STOP)
    return "OK Rotate"


def uturn(serial_file):
    reset_encoder(serial_file)
    target_rotation_180 = 49
    rotate(serial_file, 100)
    left_enc = read_encoder_l(serial_file)
    while left_enc < target_rotation_180:
        left_enc = read_encoder_l(serial_file)
        time.sleep(0.5)
    rotate(serial_file, 0)


def turn_right(serial_file, target_rotation_right):
    reset_encoder(serial_file)
    rotate(serial_file, 100)
    left_enc = read_encoder_l(serial_file)
    while left_enc < target_rotation_right:
        left_enc = read_encoder_l(serial_file)
        time.sleep(0.1)
    rotate(serial_file, 0)


def turn_left(serial_file, target_rotation_left):
    reset_encoder(serial_file)
    rotate(serial_file, -100)
    right_enc = read_encoder_r(serial_file)
    while right_enc < target_rotation_left:
        right_enc = read_encoder_r(serial_file)
        time.sleep(0.1)
    rotate(serial_file, 0)


def read_sonic(serial_file):
    write_order(serial_file, Order.READSONIC)
    while True:
        try:
            res = read_i32(serial_file)
            break
        except struct.error:
            pass
        except TimeoutError:
            write_order(serial_file, Order.READSONIC)
    return res


def read_sharp(serial_file):
    write_order(serial_file, Order.READSHARP)
    while True:
        try:
            res = read_i8(serial_file)
            break
        except struct.error:
            pass
        except TimeoutError:
            write_order(serial_file, Order.READSHARP)
    return res

def read_encoder_r(serial_file):
    write_order(serial_file, Order.READENCODERr)
    while True:
        time.sleep(.1)
        try:
            res = read_i16(serial_file)
            break
        except struct.error:
            pass
        except TimeoutError:
            write_order(serial_file, Order.READENCODERr)
    return res

def read_encoder_l(serial_file):
    write_order(serial_file, Order.READENCODERl)
    while True:
        time.sleep(.1)
        try:
            res = read_i16(serial_file)
            break
        except struct.error:
            pass
        except TimeoutError:
            write_order(serial_file, Order.READENCODERl)
    return res

def reset_encoder(serial_file):
    write_order(serial_file, Order.RESETENC)
    return "OK"

def check_obstacles(serial_file):
    front = read_sharp(serial_file)
    max_distance = 30

    return 0 < front < max_distance
