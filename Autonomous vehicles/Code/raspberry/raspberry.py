import sys
import time
import threading
import logging

# Web interface
from flask import Flask, Response, request
from flask import render_template, make_response


# Serial stuff
from robust_serial import write_order, Order, write_i8, read_i16, read_i8
from robust_serial.threads import CommandThread, ListenerThread
from robust_serial.utils import open_serial_port

# Vision analysis things
import vision
from helpers import *

# Used for image encoding and saving
import cv2

# Reduce flask messages
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Constants
BAUDRATE = 115200
step_length = 0.5
is_serial = True

# Globals
serial_file = None

# Data from the state machine controlling the bot. These are the starting values
is_automatic = False
zone_width = 300
zone_top = 150
zone_bottom = 230
speed = 100
steer_ratio = 100
# Data for intersection crossing, these are fine tuned for speed = 100
target_distance = 5
target_rotation_left = 20
target_rotation_right = 20

leave_circuit = False

current_mode = vision.MODE_FOLLOW_LINE

# We send the data to vision.py
vision.set_zone_width(zone_width)
vision.set_target_distance(target_distance)
vision.set_steer_ratio(steer_ratio)
vision.set_zone_top(zone_top)
vision.set_zone_bottom(zone_bottom)
vision.set_speed(speed)
vision.set_target_distance(target_distance)
vision.set_target_rotation_left(target_rotation_left)
vision.set_target_rotation_right(target_rotation_right)
vision.set_mode(current_mode)
vision.set_leave_circuit(leave_circuit)


def startup():
    """
        This startup code is ran before the flask server is ready to setup some interfaces like the serial.
    """
    global serial_file

    # Check sanity of the starting values.
    if zone_width > vision.IMAGE_WIDTH:
        print("Bad starting value for zone_width. You're likely to have a bug.")
    if zone_top > vision.IMAGE_HEIGHT:
        print("Bad starting value for zone_top, Your robot will behave incorrectly.")
    if zone_bottom > vision.IMAGE_HEIGHT:
        print("Bad starting value for zone_bottom, You're probably a bit tired")
    if zone_top >= zone_bottom:
        print("Zone top is bigger than zone_bottom, You've swapped the values !")
    if not (0 < speed <= 100):
        print("Bad starting value for speed. You've messed up.")

    if steer_ratio > 0:
        print("Robot will follow lines")
    elif steer_ratio == 0:
        print("Robot will ignore lines")
    else:
        print("Robot will avoid lines")

    if is_serial:
        serial_file = open_serial_port(baudrate=BAUDRATE)
        # Perform handshake with Arduino:
        print("Please wait for connection to serial ...")
        is_connected = False
        while not is_connected:
            write_order(serial_file, Order.HELLO)
            bytes_array = bytearray(serial_file.read(1))
            if not bytes_array:
                time.sleep(1)
                continue
            byte = bytes_array[0]
            if byte in [Order.HELLO.value, Order.ALREADY_CONNECTED.value]:
                is_connected = True

        print("Connected to the serial thing")
        time.sleep(1)
        serial_file.flushInput()
        print("Serial buffer flushed, ready to receive data")
    else:
        print("Serial is disabled.")


class CustomFlaskApp(Flask):
    def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
        if not self.debug or os.getenv('WERKZEUG_RUN_MAIN') == 'true':
            with self.app_context():
                startup()
        super(CustomFlaskApp, self).run(host=host, port=port,
                                        debug=debug, load_dotenv=load_dotenv, **options)


# Create the flask app !
app = CustomFlaskApp(__name__)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/auto")
def auto():
    global is_automatic
    global zone_width
    if is_automatic:
        return "already"
    start = request.args.get('start', type=tuple)
    destination = request.args.get('destination', type=tuple)
    direction = request.args.get('direction', type=str)
    isAller = request.args.get('isaller', type=str)

    # Convert coordinates to int
    destination = (int(destination[0]), int(destination[1]))
    start = (int(start[0]), int(start[1]))

    def autoFunc():
        global is_automatic
        is_automatic = True
        try:
            vision.set_need_dir_change(True)
            vision.go_to_target(serial_file,destination,start,isAller,direction)
        except Exception as err:
            print("An exception occured in automatic mode:")
            raise err
        finally:
            write_order(serial_file, Order.STOP)  # In case the thing forgot

        is_automatic = False

    t = threading.Thread(target=autoFunc, daemon=True)
    t.start()
    return "ok"


@app.route("/abort")
def abort_auto():
    global is_automatic
    if not is_automatic:
        return "not in auto"
    vision.abort_auto()
    is_automatic = False
    return "ok"


@app.route("/isauto")
def is_auto():
    global is_automatic
    if not is_automatic:
        return "false"
    return "true"


@app.route("/steer_ratio/")
def get_steer_ratio():
    return str(steer_ratio)


@app.route("/steer_ratio/<int:value>")
def set_steer_ratio(value):
    global steer_ratio
    steer_ratio = value
    vision.set_steer_ratio(value)
    return "ok"


@app.route("/zone_top")
def get_zone_top():
    return str(zone_top)
@app.route("/zone_top/<int:value>")
def set_zone_top(value):
    global zone_top
    zone_top = value
    vision.set_zone_top(value)
    return str(value)

@app.route("/manualp")
def get_manualp():
    return str(step_length)
@app.route("/manualp/<float:mode>")
def set_manualp(value):
    global step_length
    step_length = value
    return "ok"

@app.route("/zone_bottom")
def get_zone_bottom():
    return str(zone_bottom)
@app.route("/zone_bottom/<int:value>")
def set_zone_bottom(value):
    global zone_bottom
    zone_bottom = value
    vision.set_zone_bottom(value)
    return str(value)


@app.route("/zone_width")
def get_zone_width():
    return str(zone_width)
@app.route("/zone_width/<int:value>")
def set_zone_width(value):
    global zone_width
    zone_width = value
    vision.set_zone_width(value)
    return str(value)


@app.route("/speed")
def get_speed():
    return str(speed)
@app.route("/speed/<int:value>")
def set_speed(value):
    global speed
    speed = value
    vision.set_speed(value)
    return str(speed)


@app.route("/leave_circuit")
def get_leave_circuit():
    return str(leave_circuit)


@app.route("/leave_circuit/<int:value>")
def set_leave_circuit(value):
    global leave_circuit
    leave_circuit = bool(value)
    vision.set_leave_circuit(bool(value))
    return "OK"


@app.route("/target_distance")
def get_target_distance():
    return str(target_distance)


@app.route("/target_distance/<int:value>")
def set_target_distance(value):
    global target_distance
    target_distance = value
    vision.set_target_distance(value)
    return str(target_distance)


@app.route("/target_rotation_right")
def get_target_rotation_right():
    return str(target_rotation_right)


@app.route("/target_rotation_right/<int:value>")
def set_target_rotation_right(value):
    global target_rotation_right
    target_rotation_right = value
    vision.set_target_rotation_right(value)
    return str(target_rotation_right)


@app.route("/target_rotation_left")
def get_target_rotation_left():
    return str(target_rotation_left)


@app.route("/target_rotation_left/<int:value>")
def set_target_rotation_left(value):
    global target_rotation_left
    target_rotation_left = value
    vision.set_target_rotation_left(value)
    return str(target_rotation_left)


@app.route("/right")
def go_right():
    if is_automatic:
        return "auto error"
    rotate(serial_file, speed)
    time.sleep(step_length)
    write_order(serial_file, Order.STOP)
    return "ok right"


@app.route("/left")
def go_left():
    if is_automatic:
        return "auto error"
    rotate(serial_file, -speed)
    time.sleep(step_length)
    write_order(serial_file, Order.STOP)
    return "ok left"


@app.route("/forward")
def go_forward():
    if is_automatic:
        return "auto error"
    move(serial_file, speed, 0)
    time.sleep(step_length)
    write_order(serial_file, Order.STOP)
    return "ok forward"


@app.route("/backward")
def go_backward():
    if is_automatic:
        return "auto error"
    move(serial_file, -speed, 0)
    time.sleep(step_length)
    write_order(serial_file, Order.STOP)
    return "ok backward"


@app.route("/servo/<int:angle>")
def set_servo(angle):
    if is_automatic:
        return "auto error"
    # write_order(serial_file,Order.SERVO)
    # write_i16(serial_file,angle)
    # Wait till this gets implemented in helpers.py
    return "ok"

@app.route("/mode")
def get_mode():
    return str(current_mode)

@app.route("/mode/<int:mode>")
def set_mode(mode):
    global current_mode
    current_mode = mode
    vision.set_mode(current_mode)
    return str(current_mode)


@app.route("/test")
def test():
    return vision.cross_intersection(serial_file, "l")


@app.route("/pic")
def get_frame():
    """Return the content of an image that corresponds to what the camera currently sees."""
    frame = vision.get_feedback_image()
    if frame is None:
        return "cam error"  # unable to read cam.
    buffer = cv2.imencode(".jpg", frame)[1]
    response = make_response(buffer.tobytes())
    response.headers["Content-Type"] = "image/jpeg"

    return response


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", use_reloader=False)
