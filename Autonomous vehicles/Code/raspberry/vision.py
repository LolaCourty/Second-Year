from __future__ import division

from robust_serial import Order, write_order
import cv2
import numpy as np
from numpy.lib.function_base import disp
import helpers
import time

import requests
import ast
import sys

IMAGE_WIDTH = 320
IMAGE_HEIGHT = 240

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise IOError("Cannot open webcam")

cap.set(cv2.CAP_PROP_FRAME_WIDTH, IMAGE_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, IMAGE_HEIGHT)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
cap.set(cv2.CAP_PROP_FPS, 10)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)


MODE_FOLLOW_LINE = 0
MODE_GRID = 1
MODE_ROAD = 2


# These are set inside raspberry.py
zone_width = -1
zone_top = -1
zone_bottom = -1
speed = -1
steer_ratio = -1
target_distance = -1
target_rotation_left = -1
target_rotation_right = -1
current_mode = -1
leave_circuit = -1
isRunning = False
isAller = True
need_dir_change = True

current_pos = (0, 0)
previous_pos = (0, 0)
start_pos = (0, 0)
direction = "S"

server_ip = "192.168.137.1:5000"
if len(sys.argv) == 2:
    server_ip = sys.argv[1]
print("Using server IP: " + server_ip)

path = []


def display_image(img, title=""):
    cv2.imshow(title, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def compute_intersection_direction(next_coord):
    global current_pos

    """says if the robot should go right left or straight at the next intersection"""
    if next_coord[0] < current_pos[0]:
        # W
        if next_coord[1] < current_pos[1]:
            # NW
            if direction == "N":
                next_turn = "W"
            else:
                next_turn = "N"
        elif next_coord[1] == current_pos[1]:
            next_turn = "W"
        else:
            # SW
            if direction == "S":
                next_turn = "W"
            else:
                next_turn = "S"
    elif next_coord[0] == current_pos [0]:
        # N or S
        if next_coord[1] < current_pos[1]:
            next_turn = "N"
        else:
            next_turn = "S"
    else:
        # E
        if next_coord[1] < current_pos[1]:
            # NE
            if direction == "N":
                next_turn = "E"
            else:
                next_turn = "N"
        elif next_coord[1] == current_pos[1]:
            next_turn = "E"
        else:
            # SE
            if direction == "S":
                next_turn = "E"
            else:
                next_turn = "S"

    return next_turn


def cross_intersection(serial_file, intersection_direction, final=False):
    """
        Goes on the intersection and face the proper direction.
        Does not face the direction if final is set to True
    """

    # print("I'm crossing !")

    helpers.reset_encoder(serial_file)
    helpers.move(serial_file, 100, 0)
    right_enc = helpers.read_encoder_r(serial_file)
    left_enc = helpers.read_encoder_l(serial_file)

    while (right_enc+left_enc)/2 < target_distance:
        time.sleep(0.1)
        right_enc = helpers.read_encoder_r(serial_file)
        left_enc = helpers.read_encoder_l(serial_file)

    helpers.move(serial_file, 0, 0)
    helpers.reset_encoder(serial_file)

    if final:
        return  # No need to turn on the final thing.

    if intersection_direction not in ["F", "R", "B", "L"]:
        print("Bad intersection_direction: ", intersection_direction)
        print("You probably need to call this with final ? You did not provide L or R as the argument for the turning.")

    if intersection_direction == "R":
        helpers.turn_right(serial_file, target_rotation_right)
    if intersection_direction == "L":
        helpers.turn_left(serial_file, target_rotation_left)
    if intersection_direction == "R" or intersection_direction == "L":
        print(current_pos)
        time.sleep(.2)

    return str(right_enc) + "/" + str(left_enc)


def card_to_number(card_dir):
    if card_dir == "N":
        return 0
    elif card_dir == "E":
        return 1
    elif card_dir == "S":
        return 2
    else:
        return 3


def card_to_rel(card_dir):
    rel_of_card = ["F", "R", "B", "L"]  # Assuming card_dir == "N"

    shift = card_to_number(direction)

    # Shift the list
    for i in range(shift):
        rel_of_card.insert(0, rel_of_card.pop())

    return rel_of_card[card_to_number(card_dir)]


intersection_call_counter = 0
detectionCooldown = 0
obstacle_cooldown = 0


def find_intersection(img, contour, zone_left, zone_right, drive_robot, serial_file):
    global path, previous_pos, current_pos, start_pos, direction, intersection_call_counter, detectionCooldown, isAller
    intersection_call_counter += 1

    h, w = img.shape[:2]

    img = cv2.line(img, (zone_left, zone_top), (zone_right, zone_top),
                   (255, 0, 0), thickness=3)
    img = cv2.line(img, (zone_left, zone_bottom), (zone_right, zone_bottom),
                   (255, 0, 0), thickness=3)
    img = cv2.line(img, (zone_right, zone_top), (zone_right, zone_bottom),
                   (255, 0, 0), thickness=3)
    img = cv2.line(img, (zone_left, zone_top), (zone_left, zone_bottom),
                   (255, 0, 0), thickness=3)

    contour = contour[0]
    old_x = contour[0, 0, 0]
    old_y = contour[0, 0, 1]
    top_counter = 0
    right_counter = 0
    left_counter = 0
    for [[x, y]] in contour[1:]:
        if (y >= zone_top or old_y >= zone_top) and (y <= zone_bottom or old_y <= zone_bottom):
            if (zone_right <= x and zone_right >= old_x) or (zone_right >= x and zone_right <= old_x):
                # line is coming from the right
                right_counter += 1
                img = cv2.line(img, (old_x, old_y), (x, y),
                               (0, 0, 255), thickness=3)
            if (zone_left <= x and zone_left >= old_x) or (zone_left >= x and zone_left <= old_x):
                # line is coming from the left
                left_counter += 1
                img = cv2.line(img, (old_x, old_y), (x, y),
                               (0, 0, 255), thickness=3)
        if (x <= zone_right and x >= zone_left) or (old_x <= zone_right and old_x >= zone_left):
            if (y <= zone_top and old_y >= zone_top) or (y >= zone_top and old_y <= zone_top):
                # line is coming from the top
                top_counter += 1
                img = cv2.line(img, (old_x, old_y), (x, y),
                               (0, 255, 255), thickness=3)
        old_x = x
        old_y = y

    if not drive_robot:
        return img, True
    if len(path) == 0:
        return img, True  # job done.

    # print("top : ", top_counter, ", right : ",right_counter, ", left : ", left_counter)
    nb_directions = int(bool(top_counter)) + \
        int(bool(right_counter)) + int(bool(left_counter))

    detectionCooldown = max(0, detectionCooldown-1)

    if drive_robot and nb_directions > 1 and current_mode == MODE_FOLLOW_LINE:
        print("INTERSECTION DETECTED! ", detectionCooldown)

        if detectionCooldown > 0:
            return img, False
        else:
            detectionCooldown = 20

        print("top,right,left: ", bool(top_counter),
              bool(right_counter), bool(left_counter))
        helpers.move(serial_file, speed=0)

        # Used this to check what is considered as an intersection.
        # Useful if you want to know why the robot turned.
        # rm intersect*.png to clean up.
        # cv2.imwrite("intersect"+str(intersection_call_counter)+".png",img)

        next_coord = path[0]
        path = path[1:]
        print(path, current_pos)

        if len(path) == 0:
            cross_intersection(serial_file, "FINAL", True)
            print("DESTINATION REACHED!")
            previous_pos = current_pos
            current_pos = next_coord
            if isAller:
                r = requests.get('http://localhost:5000/abort')
                payload = {'start': str(current_pos[0]) + str(current_pos[1]),
                           'destination': str(start_pos[0]) + str(start_pos[1]), 'direction':"S", "isaller": "r"}
                r = requests.get('http://localhost:5000/auto', params=payload)
                need_dir_change = True

            return img,True

        next_coord = path[0]
        path = path[1:]
        intersection_direction_card = compute_intersection_direction(
            next_coord)
        intersection_direction = card_to_rel(intersection_direction_card)

        print("I'm going ", intersection_direction)
        cross_intersection(serial_file, intersection_direction)
        current_pos = next_coord
        previous_pos = current_pos
        direction = intersection_direction_card

        if len(path) == 0:
            print("DESTINATION REACHED!")
            previous_pos = current_pos
            current_pos = next_coord
            if isAller:
                r = requests.get('http://localhost:5000/abort')
                payload = {'start': str(current_pos[0]) + str(current_pos[1]),
                           'destination': str(start_pos[0]) + str(start_pos[1]), 'direction':"S", "isaller": "r"}
                r = requests.get('http://localhost:5000/auto', params=payload)
                need_dir_change = True
            return img,True

    return img, False


def center_line(img, contour, cx, cy, serial_file, drive_robot):
    h, w = img.shape[:2]
    zone_left = int(w/2) - int(zone_width/2)
    zone_right = int(w/2) + int(zone_width/2)
    tracking_line = int(w / 2)
    tracking_line_left = int(w/2) - int(zone_width/2)
    tracking_line_right = int(w/2) + int(zone_width/2)

    img = cv2.line(img, (tracking_line, 0), (tracking_line, h),
                   (0, 0, 0), thickness=2)
    img, done = find_intersection(
        img, contour, zone_left, zone_right, drive_robot, serial_file)

    if done and drive_robot:  # no need to drive robot if we've reached the target.
        return False

    if drive_robot:
        if current_mode == MODE_ROAD:
            if not leave_circuit:
                if cx > int(3*w/4):
                    # continuous line centering
                    dist = (cx - tracking_line_right)/tracking_line_right
                    ratio = -(steer_ratio/100)*dist
                else:
                    # continuous line centering
                    dist = (cx - tracking_line_left)/tracking_line_right
                    ratio = -0.75
            else:
                if cx < int(w/4):
                    # continuous line centering
                    dist = (cx - tracking_line_left)/tracking_line_right
                    ratio = -(steer_ratio/100)*dist
                else:
                    # continuous line centering
                    dist = (cx - tracking_line_left)/tracking_line_right
                    ratio = 0.75

        else:
            # continuous line centering
            dist = (cx - tracking_line)/tracking_line
            ratio = -(steer_ratio/100)*dist

        # coef is how much we slow down when turning. Put at least 30 for the effect to be noticable.
        coef = 0
        realspeed = speed - dist * coef

        helpers.move(serial_file, speed=realspeed, ratio=ratio)

    return img


def pre_processing(img):
    h, w = img.shape[:2]
    # Convert to HSV color space
    blur = cv2.blur(img, (5, 5))
    ret, thresh1 = cv2.threshold(blur, 168, 255, cv2.THRESH_BINARY)
    hsv = cv2.cvtColor(thresh1, cv2.COLOR_RGB2HSV)

    # Define range of white color in HSV
    lower_white = np.array([0, 0, 168])
    upper_white = np.array([172, 111, 255])

    # Threshold the HSV image
    mask = cv2.inRange(hsv, lower_white, upper_white)

    # Remove noise
    kernel_erode = np.ones((6, 6), np.uint8)
    eroded_mask = cv2.erode(mask, kernel_erode, iterations=1)
    kernel_dilate = np.ones((4, 4), np.uint8)
    dilated_mask = cv2.dilate(eroded_mask, kernel_dilate, iterations=1)

    return dilated_mask


def process_image(img, serial_file, drive_robot=True):
    global zone_width
    global zone_top
    h, w = img.shape[:2]

    pre_processed_img = pre_processing(img)
    # Find the different contours
    contours, hierarchy = cv2.findContours(
        pre_processed_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Sort by area (keep only the biggest one)
    contour = sorted(contours, key=cv2.contourArea, reverse=True)[:1]

    if len(contour) > 0:
        image_contour = cv2.drawContours(img, contour, 0, (0, 255, 0), 3)

        M = cv2.moments(contour[0])
        # Centroid
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        processed_image = cv2.circle(
            image_contour, (cx, cy), 20, (255, 0, 0), 2)
        processed_image = center_line(
            processed_image, contour, cx, cy, serial_file, drive_robot)
        return processed_image

    else:
        return img


def request_path_from_server(current_pos, dest_post):
    current_pos = str(current_pos[0])+str(current_pos[1])
    dest_post = str(dest_post[0])+str(dest_post[1])
    payload = {'start': current_pos, 'destination': dest_post}
    r = requests.get('http://'+server_ip+"/initial_path", params=payload)
    path = ast.literal_eval(r.text)
    print(path)
    return path

def add_obstacle_to_server(obstacle, current_pos, dest_post):
    obstacle = str(obstacle[0])+str(obstacle[1])
    current_pos = str(current_pos[0])+str(current_pos[1])
    dest_post = str(dest_post[0])+str(dest_post[1])
    payload = {'obstacle': obstacle,
               'start': current_pos, 'destination': dest_post}
    r = requests.get('http://'+server_ip+"/add_obstacle", params=payload)
    try:
        path = ast.literal_eval(r.text)
    except Exception:  # The server should not find a valid path, stopping.
        print("Invalid server response. Stopping !")
        print(path)
        path = []
    print(path)
    return path

def go_to_target(serial_file, dest_post, start_posCalled, isAllerCalled, start_direction = "N"):
    global isRunning
    global current_pos, direction
    global path
    global detectionCooldown
    global need_dir_change
    global isAller
    global start_pos
    global obstacle_cooldown

    start_pos = start_posCalled
    if isAllerCalled == "a":
        isAller = True
    else:
        isAller = False

    detectionCooldown = 0 # No cooldown at the beginning
    isRunning = True
    # isRunning is set to False in abort_auto

    current_pos = start_pos
    direction = start_direction
    path = request_path_from_server(current_pos, dest_post)

    while isRunning:
        if need_dir_change:
            # print("Current direction:", direction)
            # print("Current position:", current_pos, "Next position:", path[0])
            correct_card_dir = compute_intersection_direction(path[0])
            # print("Correct card_dir :", correct_card_dir)
            correct_rel_dir = card_to_rel(correct_card_dir)
            # print("Correct rel_dir:", correct_rel_dir)
            # The current rel_dir is tautologically forward
            print("need_dir: Turning " + correct_rel_dir)
            if correct_rel_dir == "R":
                helpers.turn_right(serial_file, target_rotation_right)
            elif correct_rel_dir == "B":
                helpers.uturn(serial_file)
            elif correct_rel_dir == "L":
                helpers.turn_left(serial_file, target_rotation_left)
            need_dir_change = False
        
        if current_mode == -1:
            print("No mode is set, ignoring command")
            break

        ret, frame = cap.read()
        if frame is not None:
            obstacle_cooldown = max(0, obstacle_cooldown - 1)
            if helpers.check_obstacles(serial_file):
                print("Obstacle detected")
                if current_pos[0] % 2 or current_pos[1] % 2:
                    # The current position is not an intersection
                    # The obstacle is thus at the current position
                    obstacle = current_pos
                else:
                    # The current position is an intersection
                    # The obstacle is thus in the next position
                    obstacle = path[0]
                write_order(serial_file, Order.STOP)
                # The robot goes to the previous position (first element in the new path)
                # and continues using a new path
                path = add_obstacle_to_server(
                    obstacle, previous_pos, dest_post)

            frame = process_image(frame, serial_file, True)
            if frame is False:
                break
        else:
            print("Unable to access camera!!")
            break


def get_feedback_image():

    ret, frame = cap.read()
    if frame is None:
        return
    frame = process_image(frame, None, False)
    return frame


def set_mode(m):
    global current_mode
    current_mode = m


def abort_auto():
    global isRunning
    isRunning = False


def set_zone_width(w):
    global zone_width
    zone_width = w


def set_target_distance(d):
    global target_distance
    target_distance = d


def set_target_rotation_right(rr):
    global target_rotation_right
    target_rotation_right = rr


def set_target_rotation_left(rl):
    global target_rotation_left
    target_rotation_left = rl


def set_steer_ratio(r):
    global steer_ratio
    steer_ratio = r


def set_zone_top(t):
    global zone_top
    zone_top = t


def set_zone_bottom(t):
    global zone_bottom
    zone_bottom = t


def set_leave_circuit(b):
    global leave_circuit
    leave_circuit = b


def set_speed(s):
    global speed
    speed = s

def set_need_dir_change(val):
    global need_dir_change
    need_dir_change = val

def set_isAller(val):
    global isAller
    isAller = val

if __name__ == "__main__":
    img = get_feedback_image()
    display_image(img)
